"""
Fix Agent - Generates code fixes for accessibility violations.

Takes scan results from the Scanner Agent and produces
actionable, copy-paste-ready code fixes for each violation.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.base import BaseAgent
from app.ai_suggestions import RULE_FIXES


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

    def get_tools(self):
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

    def _handle_tool(self, tool_name, tool_input):
        if tool_name == "get_rule_fix":
            return self._get_rule_fix(tool_input["rule_id"])
        elif tool_name == "generate_fixes":
            return self._generate_fixes(tool_input["violations"])
        return {"error": f"Unknown tool: {tool_name}"}

    def _get_rule_fix(self, rule_id):
        """Get the standard fix for a rule."""
        fix = RULE_FIXES.get(rule_id)
        if fix:
            return {
                "rule_id": rule_id,
                "explanation": fix["explanation"],
                "fix_template": fix["fix_template"],
            }
        return {"error": f"No fix template for rule: {rule_id}"}

    def _generate_fixes(self, violations):
        """Generate fixes for a batch of violations."""
        EFFORT_MAP = {
            "img-alt": {"effort": "Quick (2-5 min)", "minutes": 5},
            "form-label": {"effort": "Quick (5-10 min)", "minutes": 10},
            "html-lang": {"effort": "Quick (1 min)", "minutes": 1},
            "page-title": {"effort": "Quick (1-2 min)", "minutes": 2},
            "empty-link": {"effort": "Quick (3-5 min)", "minutes": 5},
            "empty-button": {"effort": "Quick (3-5 min)", "minutes": 5},
            "heading-order": {"effort": "Moderate (10-20 min)", "minutes": 15},
            "skip-nav": {"effort": "Quick (5 min)", "minutes": 5},
            "landmark-main": {"effort": "Moderate (5-15 min)", "minutes": 10},
            "meta-viewport": {"effort": "Quick (1 min)", "minutes": 1},
        }

        fixes = []
        total_minutes = 0

        for v in violations:
            rule_id = v.get("rule_id", "")
            rule_fix = RULE_FIXES.get(rule_id, {})
            effort_info = EFFORT_MAP.get(rule_id, {"effort": "Moderate (10 min)", "minutes": 10})

            fix_entry = {
                "rule_id": rule_id,
                "page_url": v.get("page_url", ""),
                "element_html": v.get("element_html", ""),
                "explanation": rule_fix.get("explanation", v.get("description", "")),
                "fix_template": rule_fix.get("fix_template", "Review and fix according to WCAG 2.2 guidelines."),
                "effort": effort_info["effort"],
                "effort_minutes": effort_info["minutes"],
            }
            fixes.append(fix_entry)
            total_minutes += effort_info["minutes"]

        return {
            "fixes": fixes,
            "total_fixes": len(fixes),
            "total_effort_minutes": total_minutes,
            "total_effort_display": f"{total_minutes // 60}h {total_minutes % 60}m" if total_minutes >= 60 else f"{total_minutes} min",
        }
