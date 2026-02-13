"""
Base agent class for the PageGuard multi-agent system.
Each agent wraps the Anthropic API with a specific role and tool set.
"""

import json
import logging
import time
from typing import Any, Optional

import anthropic

from agents.constants import ANTHROPIC_MODEL, MAX_AGENT_ITERATIONS, AGENT_API_TIMEOUT

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all PageGuard agents."""

    name: str = "base"
    role: str = "assistant"
    system_prompt: str = "You are a helpful assistant."

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model or ANTHROPIC_MODEL
        self.conversation: list[dict] = []
        self.tools: list[dict] = []

    def get_tools(self) -> list[dict]:
        """Return tool definitions for this agent. Override in subclasses."""
        return self.tools

    def run(self, task: str, context: Optional[dict] = None) -> dict[str, Any]:
        """Execute the agent's task with an agentic tool-use loop."""
        messages: list[dict] = [{"role": "user", "content": self._build_prompt(task, context)}]
        tools = self.get_tools()

        response = None
        for iteration in range(MAX_AGENT_ITERATIONS):
            kwargs: dict[str, Any] = {
                "model": self.model,
                "max_tokens": 4096,
                "system": self.system_prompt,
                "messages": messages,
                "timeout": AGENT_API_TIMEOUT,
            }
            if tools:
                kwargs["tools"] = tools

            try:
                response = self.client.messages.create(**kwargs)
            except anthropic.RateLimitError:
                wait = min(2 ** iteration, 16)
                logger.warning("[%s] Rate limited, retrying in %ds", self.name, wait)
                time.sleep(wait)
                continue
            except anthropic.APIConnectionError as e:
                logger.error("[%s] API connection error: %s", self.name, e)
                return {"text": f"Agent connection error: {e}", "agent": self.name, "error": True}
            except anthropic.AuthenticationError as e:
                logger.error("[%s] Authentication error: %s", self.name, e)
                return {"text": "Invalid API key. Check ANTHROPIC_API_KEY.", "agent": self.name, "error": True}
            except anthropic.APIError as e:
                logger.error("[%s] API error on iteration %d: %s", self.name, iteration, e)
                return {"text": f"Agent API error: {e}", "agent": self.name, "error": True}

            # Collect response
            assistant_content = response.content
            messages.append({"role": "assistant", "content": assistant_content})

            # Handle tool calls
            if response.stop_reason == "tool_use":
                tool_results = []
                for block in assistant_content:
                    if block.type == "tool_use":
                        logger.info("[%s] Calling tool: %s", self.name, block.name)
                        try:
                            result = self._handle_tool(block.name, block.input)
                        except Exception as e:
                            logger.error("[%s] Tool %s failed: %s", self.name, block.name, e)
                            result = {"error": f"Tool execution failed: {e}"}
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result, default=str) if isinstance(result, (dict, list)) else str(result),
                        })
                messages.append({"role": "user", "content": tool_results})
            else:
                break
        else:
            logger.warning("[%s] Hit max iterations (%d)", self.name, MAX_AGENT_ITERATIONS)

        # Extract final text response
        if response is None:
            return {"text": "Agent failed to get a response after retries.", "agent": self.name, "error": True}

        final_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                final_text += block.text

        if not final_text:
            logger.warning("[%s] Agent returned no text content", self.name)

        return {"text": final_text, "agent": self.name, "error": False}

    def _build_prompt(self, task: str, context: Optional[dict] = None) -> str:
        """Build the full prompt with context."""
        parts = [task]
        if context:
            # Truncate large context values to prevent token overflow
            truncated = {}
            for key, value in context.items():
                if isinstance(value, str) and len(value) > 4000:
                    truncated[key] = value[:4000] + "\n... (truncated)"
                    logger.info("[%s] Truncated context key '%s' from %d to 4000 chars", self.name, key, len(value))
                else:
                    truncated[key] = value
            parts.insert(0, f"Context from other agents:\n```json\n{json.dumps(truncated, indent=2, ensure_ascii=False, default=str)}\n```\n")
        return "\n\n".join(parts)

    def _handle_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Handle a tool call. Override in subclasses for custom tools."""
        return {"error": f"Unknown tool: {tool_name}"}
