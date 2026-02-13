"""
Base agent class for the PageGuard multi-agent system.
Each agent wraps the Anthropic API with a specific role and tool set.
"""

import json
import anthropic


class BaseAgent:
    """Base class for all PageGuard agents."""

    name: str = "base"
    role: str = "assistant"
    system_prompt: str = "You are a helpful assistant."
    model: str = "claude-sonnet-4-5-20250929"

    def __init__(self, api_key: str = None):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.conversation: list = []
        self.tools: list = []

    def get_tools(self) -> list:
        """Return tool definitions for this agent. Override in subclasses."""
        return self.tools

    def run(self, task: str, context: dict = None) -> dict:
        """Execute the agent's task with an agentic tool-use loop."""
        messages = [{"role": "user", "content": self._build_prompt(task, context)}]
        tools = self.get_tools()

        max_iterations = 10
        for _ in range(max_iterations):
            kwargs = {
                "model": self.model,
                "max_tokens": 4096,
                "system": self.system_prompt,
                "messages": messages,
            }
            if tools:
                kwargs["tools"] = tools

            response = self.client.messages.create(**kwargs)

            # Collect text and tool use blocks
            assistant_content = response.content
            messages.append({"role": "assistant", "content": assistant_content})

            # Check if we need to handle tool calls
            if response.stop_reason == "tool_use":
                tool_results = []
                for block in assistant_content:
                    if block.type == "tool_use":
                        result = self._handle_tool(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result) if isinstance(result, (dict, list)) else str(result),
                        })
                messages.append({"role": "user", "content": tool_results})
            else:
                # Agent finished - extract final text
                break

        # Extract final text response
        final_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                final_text += block.text

        return {"text": final_text, "agent": self.name}

    def _build_prompt(self, task: str, context: dict = None) -> str:
        """Build the full prompt with context."""
        parts = [task]
        if context:
            parts.insert(0, f"Context from other agents:\n```json\n{json.dumps(context, indent=2, ensure_ascii=False)}\n```\n")
        return "\n\n".join(parts)

    def _handle_tool(self, tool_name: str, tool_input: dict):
        """Handle a tool call. Override in subclasses for custom tools."""
        return {"error": f"Unknown tool: {tool_name}"}
