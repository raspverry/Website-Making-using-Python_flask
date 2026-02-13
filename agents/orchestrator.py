"""
Orchestrator Agent - Coordinates the multi-agent team.

The Orchestrator manages the workflow between Scanner, Fix, and Report agents.
It delegates tasks, passes context between agents, and aggregates final results.

Workflow:
    1. Scanner Agent → crawls site, finds violations
    2. Fix Agent → generates fixes for each violation
    3. Report Agent → creates compliance report
    4. Orchestrator → aggregates and presents final results
"""

import json
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.base import BaseAgent
from agents.scanner_agent import ScannerAgent
from agents.fix_agent import FixAgent
from agents.report_agent import ReportAgent


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

    def __init__(self, api_key=None):
        super().__init__(api_key=api_key)
        self.scanner = ScannerAgent(api_key=api_key)
        self.fixer = FixAgent(api_key=api_key)
        self.reporter = ReportAgent(api_key=api_key)
        self._scan_results = {}
        self._fix_results = {}
        self._report_results = {}

    def get_tools(self):
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
                        "task": {
                            "type": "string",
                            "description": "Description of what fixes to generate",
                        },
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
                        "task": {
                            "type": "string",
                            "description": "Description of what report to generate",
                        },
                    },
                    "required": ["task"],
                },
            },
        ]

    def _handle_tool(self, tool_name, tool_input):
        if tool_name == "delegate_to_scanner":
            return self._delegate_scanner(tool_input)
        elif tool_name == "delegate_to_fixer":
            return self._delegate_fixer(tool_input)
        elif tool_name == "delegate_to_reporter":
            return self._delegate_reporter(tool_input)
        return {"error": f"Unknown tool: {tool_name}"}

    def _delegate_scanner(self, tool_input):
        """Delegate to Scanner Agent."""
        url = tool_input["url"]
        max_pages = tool_input.get("max_pages", 5)

        print(f"\n[Orchestrator] Delegating to Scanner Agent: {url}")
        result = self.scanner.run(
            task=f"Scan the website {url} for WCAG 2.2 Level AA accessibility violations. Scan up to {max_pages} pages.",
        )
        self._scan_results = result
        print(f"[Orchestrator] Scanner Agent completed")
        return {"agent": "scanner", "result": result["text"][:3000]}

    def _delegate_fixer(self, tool_input):
        """Delegate to Fix Agent with scan context."""
        task = tool_input.get("task", "Generate fixes for all violations found")

        context = {}
        if self._scan_results:
            context["scan_results"] = self._scan_results.get("text", "")[:2000]

        print(f"\n[Orchestrator] Delegating to Fix Agent")
        result = self.fixer.run(task=task, context=context)
        self._fix_results = result
        print(f"[Orchestrator] Fix Agent completed")
        return {"agent": "fixer", "result": result["text"][:3000]}

    def _delegate_reporter(self, tool_input):
        """Delegate to Report Agent with scan + fix context."""
        task = tool_input.get("task", "Generate a compliance report")

        context = {}
        if self._scan_results:
            context["scan_results"] = self._scan_results.get("text", "")[:2000]
        if self._fix_results:
            context["fix_suggestions"] = self._fix_results.get("text", "")[:2000]

        print(f"\n[Orchestrator] Delegating to Report Agent")
        result = self.reporter.run(task=task, context=context)
        self._report_results = result
        print(f"[Orchestrator] Report Agent completed")
        return {"agent": "reporter", "result": result["text"][:3000]}

    def run_full_audit(self, url, max_pages=5):
        """Run a complete multi-agent accessibility audit.

        This is a direct (non-LLM) orchestration method that runs
        all three agents in sequence without requiring an API call
        to the orchestrator itself. Use this for programmatic access.
        """
        results = {"url": url, "agents": {}}

        # Step 1: Scanner Agent
        print(f"\n{'='*60}")
        print(f"  PAGEGUARD MULTI-AGENT ACCESSIBILITY AUDIT")
        print(f"  URL: {url}")
        print(f"{'='*60}")

        print(f"\n[Step 1/3] Scanner Agent analyzing {url}...")
        start = time.time()
        scan_result = self.scanner.run(
            task=f"Scan {url} for all WCAG 2.2 Level AA violations. Scan up to {max_pages} pages. Report all violations found with severity ratings."
        )
        results["agents"]["scanner"] = {
            "output": scan_result["text"],
            "duration": round(time.time() - start, 1),
        }
        print(f"    Done in {results['agents']['scanner']['duration']}s")

        # Step 2: Fix Agent
        print(f"\n[Step 2/3] Fix Agent generating remediation code...")
        start = time.time()
        fix_result = self.fixer.run(
            task="Generate specific code fixes for each violation. Show before/after HTML and estimate effort.",
            context={"scan_results": scan_result["text"][:3000]},
        )
        results["agents"]["fixer"] = {
            "output": fix_result["text"],
            "duration": round(time.time() - start, 1),
        }
        print(f"    Done in {results['agents']['fixer']['duration']}s")

        # Step 3: Report Agent
        print(f"\n[Step 3/3] Report Agent creating compliance report...")
        start = time.time()
        report_result = self.reporter.run(
            task="Create a comprehensive accessibility compliance report with risk assessment and prioritized remediation plan.",
            context={
                "scan_results": scan_result["text"][:2000],
                "fix_suggestions": fix_result["text"][:2000],
            },
        )
        results["agents"]["reporter"] = {
            "output": report_result["text"],
            "duration": round(time.time() - start, 1),
        }
        print(f"    Done in {results['agents']['reporter']['duration']}s")

        print(f"\n{'='*60}")
        print(f"  AUDIT COMPLETE")
        print(f"{'='*60}\n")

        return results
