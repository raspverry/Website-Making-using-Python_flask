"""
Orchestrator Agent - Coordinates the multi-agent team.

The Orchestrator manages the workflow between Scanner, Fix, and Report agents.
It delegates tasks, passes context between agents, and aggregates final results.

Workflow:
    1. Scanner Agent -> crawls site, finds violations
    2. Fix Agent -> generates fixes for each violation
    3. Report Agent -> creates compliance report
    4. Orchestrator -> aggregates and presents final results
"""

import logging
import time
from typing import Any, Optional

from agents.base import BaseAgent
from agents.scanner_agent import ScannerAgent
from agents.fix_agent import FixAgent
from agents.report_agent import ReportAgent
from agents.constants import MAX_CONTEXT_LENGTH

logger = logging.getLogger(__name__)


class OrchestratorAgent(BaseAgent):
    name = "orchestrator"
    role = "Team Coordinator"
    system_prompt = """You are the Orchestrator Agent for PageGuard's multi-agent accessibility audit system.

You coordinate a team of specialized agents:
1. Scanner Agent: Crawls websites and detects WCAG 2.2 violations
2. Fix Agent: Generates code fixes for violations
3. Report Agent: Creates compliance reports and risk assessments

Your workflow:
1. Use delegate_to_scanner to scan the website
2. Use delegate_to_fixer with the scan results to get fixes
3. Use delegate_to_reporter with scan + fix data to generate a report
4. Synthesize all results into a clear, actionable summary for the user

Always follow this order. Present the final results clearly with:
- Overall compliance score
- Key violations found
- Prioritized fix list
- Risk assessment
- Estimated remediation effort"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        super().__init__(api_key=api_key, model=model)
        self.scanner = ScannerAgent(api_key=api_key, model=model)
        self.fixer = FixAgent(api_key=api_key, model=model)
        self.reporter = ReportAgent(api_key=api_key, model=model)
        self._scan_results: dict = {}
        self._fix_results: dict = {}
        self._report_results: dict = {}

    def get_tools(self) -> list[dict]:
        return [
            {
                "name": "delegate_to_scanner",
                "description": "Delegate website scanning to the Scanner Agent. It will crawl the website and find all WCAG 2.2 Level AA violations.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "The website URL to scan"},
                        "max_pages": {"type": "integer", "description": "Maximum pages to scan", "default": 5},
                    },
                    "required": ["url"],
                },
            },
            {
                "name": "delegate_to_fixer",
                "description": "Delegate fix generation to the Fix Agent. Pass the violations found by the Scanner Agent.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task": {"type": "string", "description": "Description of what fixes to generate"},
                    },
                    "required": ["task"],
                },
            },
            {
                "name": "delegate_to_reporter",
                "description": "Delegate report generation to the Report Agent. It will create a compliance report using scan and fix data.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task": {"type": "string", "description": "Description of what report to generate"},
                    },
                    "required": ["task"],
                },
            },
        ]

    def _handle_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "delegate_to_scanner":
            return self._delegate_scanner(tool_input)
        elif tool_name == "delegate_to_fixer":
            return self._delegate_fixer(tool_input)
        elif tool_name == "delegate_to_reporter":
            return self._delegate_reporter(tool_input)
        return {"error": f"Unknown tool: {tool_name}"}

    def _delegate_scanner(self, tool_input: dict) -> dict:
        """Delegate to Scanner Agent."""
        url = tool_input["url"]
        max_pages = tool_input.get("max_pages", 5)

        logger.info("[orchestrator] Delegating to Scanner Agent: %s", url)
        result = self.scanner.run(
            task=f"Scan the website {url} for WCAG 2.2 Level AA accessibility violations. Scan up to {max_pages} pages.",
        )

        if result.get("error"):
            logger.error("[orchestrator] Scanner Agent failed: %s", result.get("text"))
            return {"agent": "scanner", "error": result["text"]}

        self._scan_results = result
        text = result.get("text", "")
        if len(text) > MAX_CONTEXT_LENGTH:
            logger.info("[orchestrator] Truncating scanner output from %d to %d chars", len(text), MAX_CONTEXT_LENGTH)
        return {"agent": "scanner", "result": text[:MAX_CONTEXT_LENGTH]}

    def _delegate_fixer(self, tool_input: dict) -> dict:
        """Delegate to Fix Agent with scan context."""
        task = tool_input.get("task", "Generate fixes for all violations found")

        context = {}
        if self._scan_results:
            context["scan_results"] = self._scan_results.get("text", "")[:MAX_CONTEXT_LENGTH]

        logger.info("[orchestrator] Delegating to Fix Agent")
        result = self.fixer.run(task=task, context=context)

        if result.get("error"):
            logger.error("[orchestrator] Fix Agent failed: %s", result.get("text"))
            return {"agent": "fixer", "error": result["text"]}

        self._fix_results = result
        text = result.get("text", "")
        return {"agent": "fixer", "result": text[:MAX_CONTEXT_LENGTH]}

    def _delegate_reporter(self, tool_input: dict) -> dict:
        """Delegate to Report Agent with scan + fix context."""
        task = tool_input.get("task", "Generate a compliance report")
        half_context = MAX_CONTEXT_LENGTH // 2

        context = {}
        if self._scan_results:
            context["scan_results"] = self._scan_results.get("text", "")[:half_context]
        if self._fix_results:
            context["fix_suggestions"] = self._fix_results.get("text", "")[:half_context]

        logger.info("[orchestrator] Delegating to Report Agent")
        result = self.reporter.run(task=task, context=context)

        if result.get("error"):
            logger.error("[orchestrator] Report Agent failed: %s", result.get("text"))
            return {"agent": "reporter", "error": result["text"]}

        self._report_results = result
        text = result.get("text", "")
        return {"agent": "reporter", "result": text[:MAX_CONTEXT_LENGTH]}

    def run_full_audit(self, url: str, max_pages: int = 5) -> dict:
        """Run a complete multi-agent accessibility audit.

        Direct orchestration method that runs all three agents in sequence
        without requiring an API call to the orchestrator itself.
        """
        results: dict[str, Any] = {"url": url, "agents": {}}

        logger.info("Starting multi-agent audit for %s", url)

        # Step 1: Scanner Agent
        logger.info("[Step 1/3] Scanner Agent analyzing %s", url)
        start = time.time()
        scan_result = self.scanner.run(
            task=f"Scan {url} for all WCAG 2.2 Level AA violations. Scan up to {max_pages} pages. Report all violations found with severity ratings."
        )
        duration = round(time.time() - start, 1)
        results["agents"]["scanner"] = {
            "output": scan_result["text"],
            "duration": duration,
            "error": scan_result.get("error", False),
        }
        logger.info("[Step 1/3] Scanner Agent completed in %ss", duration)

        # Step 2: Fix Agent
        logger.info("[Step 2/3] Fix Agent generating remediation code")
        start = time.time()
        fix_result = self.fixer.run(
            task="Generate specific code fixes for each violation. Show before/after HTML and estimate effort.",
            context={"scan_results": scan_result["text"][:MAX_CONTEXT_LENGTH]},
        )
        duration = round(time.time() - start, 1)
        results["agents"]["fixer"] = {
            "output": fix_result["text"],
            "duration": duration,
            "error": fix_result.get("error", False),
        }
        logger.info("[Step 2/3] Fix Agent completed in %ss", duration)

        # Step 3: Report Agent
        half = MAX_CONTEXT_LENGTH // 2
        logger.info("[Step 3/3] Report Agent creating compliance report")
        start = time.time()
        report_result = self.reporter.run(
            task="Create a comprehensive accessibility compliance report with risk assessment and prioritized remediation plan.",
            context={
                "scan_results": scan_result["text"][:half],
                "fix_suggestions": fix_result["text"][:half],
            },
        )
        duration = round(time.time() - start, 1)
        results["agents"]["reporter"] = {
            "output": report_result["text"],
            "duration": duration,
            "error": report_result.get("error", False),
        }
        logger.info("[Step 3/3] Report Agent completed in %ss", duration)
        logger.info("Multi-agent audit complete for %s", url)

        return results
