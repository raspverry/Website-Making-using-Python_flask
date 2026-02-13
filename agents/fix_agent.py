"""
Fix Agent - Generates code fixes for accessibility violations.

Takes scan results from the Scanner Agent and produces
actionable, copy-paste-ready code fixes for each violation.
"""

import logging
from typing import Any

from agents.base import BaseAgent
from agents.constants import EFFORT_ESTIMATES, DEFAULT_EFFORT, format_effort, get_effort_for_rule

logger = logging.getLogger(__name__)


def _import_rule_fixes():
    """Import rule fixes from backend AI service."""
    from backend.services.ai_service import RULE_FIXES
    return RULE_FIXES


class FixAgent(BaseAgent):
    name = "fixer"
    role = "Accessibility Fix Generator"
    system_prompt = """You are the Fix Agent for PageGuard, an expert in web accessibility remediation.

Your role:
1. Receive violation data from the Scanner Agent
2. Generate specific, actionable code fixes for each violation
3. Show before/after HTML examples
4. Estimate effort for each fix (minutes)
5. Prioritize fixes by impact (critical first)

You have access to these tools:
- get_rule_fix: Get the standard fix template for a WCAG rule
- generate_fixes: Generate fixes for a batch of violations

Guidelines:
- Always provide copy-paste-ready code
- Show before (broken) and after (fixed) HTML
- Keep explanations simple for non-technical users
- Group related fixes together (e.g., all img-alt fixes)
- Estimate effort: Quick (1-5 min), Moderate (10-30 min), Complex (30+ min)"""

    def get_tools(self) -> list[dict]:
        return [
            {
                "name": "get_rule_fix",
                "description": "Get the standard fix template and explanation for a specific WCAG rule violation.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "rule_id": {
                            "type": "string",
                            "description": "The rule ID (e.g., 'img-alt', 'form-label', 'html-lang')",
                        },
                    },
                    "required": ["rule_id"],
                },
            },
            {
                "name": "generate_fixes",
                "description": "Generate fixes for a batch of violations. Returns fix suggestions with before/after code and effort estimates.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "violations": {
                            "type": "array",
                            "description": "List of violations to fix",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "rule_id": {"type": "string"},
                                    "description": {"type": "string"},
                                    "element_html": {"type": "string"},
                                    "page_url": {"type": "string"},
                                },
                            },
                        },
                    },
                    "required": ["violations"],
                },
            },
        ]

    def _handle_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "get_rule_fix":
            return self._get_rule_fix(tool_input["rule_id"])
        elif tool_name == "generate_fixes":
            return self._generate_fixes(tool_input["violations"])
        return {"error": f"Unknown tool: {tool_name}"}

    def _get_rule_fix(self, rule_id: str) -> dict:
        """Get the standard fix for a rule."""
        rule_fixes = _import_rule_fixes()
        fix = rule_fixes.get(rule_id)
        if fix:
            effort = get_effort_for_rule(rule_id)
            return {
                "rule_id": rule_id,
                "explanation": fix["explanation"],
                "fix_template": fix["fix_template"],
                "effort": effort["label"],
                "effort_minutes": effort["max"],
            }
        logger.warning("[fixer] No fix template for rule: %s", rule_id)
        return {
            "rule_id": rule_id,
            "explanation": "Review and fix according to WCAG 2.2 guidelines.",
            "fix_template": "Consult WCAG 2.2 documentation for this rule.",
            "effort": DEFAULT_EFFORT["label"],
            "effort_minutes": DEFAULT_EFFORT["max"],
        }

    def _generate_fixes(self, violations: list[dict]) -> dict:
        """Generate fixes for a batch of violations."""
        rule_fixes = _import_rule_fixes()
        fixes = []
        total_minutes = 0

        for v in violations:
            rule_id = v.get("rule_id", "")
            rule_fix = rule_fixes.get(rule_id, {})
            effort = get_effort_for_rule(rule_id)

            fix_entry = {
                "rule_id": rule_id,
                "page_url": v.get("page_url", ""),
                "element_html": v.get("element_html", ""),
                "explanation": rule_fix.get("explanation", v.get("description", "")),
                "fix_template": rule_fix.get("fix_template", "Review and fix according to WCAG 2.2 guidelines."),
                "effort": effort["label"],
                "effort_minutes": effort["max"],
            }
            fixes.append(fix_entry)
            total_minutes += effort["max"]

        return {
            "fixes": fixes,
            "total_fixes": len(fixes),
            "total_effort_minutes": total_minutes,
            "total_effort_display": format_effort(total_minutes),
        }
