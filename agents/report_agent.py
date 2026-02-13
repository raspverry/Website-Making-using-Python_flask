"""
Report Agent - Creates executive summaries and compliance reports.

Takes results from Scanner and Fix agents to produce
professional accessibility compliance reports.
"""

import json
from datetime import datetime

from agents.base import BaseAgent


class ReportAgent(BaseAgent):
    name = "reporter"
    role = "Compliance Report Generator"
    system_prompt = """You are the Report Agent for PageGuard, an expert in accessibility compliance reporting.

Your role:
1. Receive scan results and fix suggestions from other agents
2. Create a professional executive summary
3. Build a structured compliance report
4. Assess legal risk based on ADA Title II deadline (April 24, 2026)
5. Provide clear, actionable recommendations

You have access to these tools:
- generate_report: Create a full compliance report from scan data
- assess_risk: Evaluate legal/compliance risk level

Guidelines:
- Write in clear, non-technical language that business owners can understand
- Always reference the ADA Title II deadline when relevant
- Include specific violation counts and severity breakdown
- Provide a prioritized remediation roadmap
- Estimate total remediation effort in hours"""

    def get_tools(self):
        return [
            {
                "name": "generate_report",
                "description": "Generate a comprehensive accessibility compliance report from scan results and fix suggestions.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Website URL that was scanned"},
                        "score": {"type": "integer", "description": "Compliance score 0-100"},
                        "total_violations": {"type": "integer"},
                        "critical_count": {"type": "integer"},
                        "serious_count": {"type": "integer"},
                        "moderate_count": {"type": "integer"},
                        "minor_count": {"type": "integer"},
                        "pages_scanned": {"type": "integer"},
                        "violations_summary": {
                            "type": "array",
                            "description": "Summary of violations by rule",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "rule_id": {"type": "string"},
                                    "rule_name": {"type": "string"},
                                    "severity": {"type": "string"},
                                    "count": {"type": "integer"},
                                },
                            },
                        },
                        "total_effort_minutes": {"type": "integer", "description": "Estimated total fix time in minutes"},
                    },
                    "required": ["url", "score", "total_violations"],
                },
            },
            {
                "name": "assess_risk",
                "description": "Assess legal and compliance risk level based on scan results.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "integer", "description": "Compliance score 0-100"},
                        "critical_count": {"type": "integer"},
                        "serious_count": {"type": "integer"},
                    },
                    "required": ["score"],
                },
            },
        ]

    def _handle_tool(self, tool_name, tool_input):
        if tool_name == "generate_report":
            return self._generate_report(tool_input)
        elif tool_name == "assess_risk":
            return self._assess_risk(tool_input)
        return {"error": f"Unknown tool: {tool_name}"}

    def _generate_report(self, data):
        """Generate a structured compliance report."""
        score = data.get("score", 0)
        url = data.get("url", "Unknown")
        total = data.get("total_violations", 0)
        critical = data.get("critical_count", 0)
        serious = data.get("serious_count", 0)
        moderate = data.get("moderate_count", 0)
        minor = data.get("minor_count", 0)
        pages = data.get("pages_scanned", 0)
        effort = data.get("total_effort_minutes", 0)
        violations_summary = data.get("violations_summary", [])

        # Determine compliance status
        if score >= 90:
            status = "Likely Compliant"
            status_color = "green"
        elif score >= 70:
            status = "Needs Improvement"
            status_color = "yellow"
        elif score >= 50:
            status = "At Risk"
            status_color = "orange"
        else:
            status = "Non-Compliant"
            status_color = "red"

        # Build violation breakdown
        by_rule = {}
        for v in violations_summary:
            rule_id = v.get("rule_id", "unknown")
            if rule_id not in by_rule:
                by_rule[rule_id] = {
                    "rule_name": v.get("rule_name", rule_id),
                    "severity": v.get("severity", "unknown"),
                    "count": 0,
                }
            by_rule[rule_id]["count"] += v.get("count", 1)

        # Calculate days until ADA deadline
        deadline = datetime(2026, 4, 24)
        days_remaining = (deadline - datetime.now()).days

        report = {
            "title": f"Web Accessibility Compliance Report - {url}",
            "generated_at": datetime.now().isoformat(),
            "website": url,
            "summary": {
                "compliance_score": score,
                "compliance_status": status,
                "status_color": status_color,
                "total_violations": total,
                "pages_scanned": pages,
                "severity_breakdown": {
                    "critical": critical,
                    "serious": serious,
                    "moderate": moderate,
                    "minor": minor,
                },
            },
            "risk_assessment": {
                "ada_deadline": "April 24, 2026",
                "days_remaining": max(0, days_remaining),
                "risk_level": "HIGH" if score < 50 else "MEDIUM" if score < 80 else "LOW",
                "max_penalty": "$75,000 first violation, $150,000 subsequent",
            },
            "violations_by_rule": by_rule,
            "remediation": {
                "estimated_effort_minutes": effort,
                "estimated_effort_display": f"{effort // 60}h {effort % 60}m" if effort >= 60 else f"{effort} min",
                "priority_order": [
                    "1. Fix all critical violations (alt text, form labels, viewport zoom)",
                    "2. Fix serious violations (page language, empty links/buttons)",
                    "3. Fix moderate violations (heading structure, skip navigation, landmarks)",
                    "4. Re-scan to verify fixes",
                    "5. Schedule regular monitoring scans",
                ],
            },
            "recommendations": self._get_recommendations(score, critical, serious),
        }

        return report

    def _assess_risk(self, data):
        """Assess legal/compliance risk."""
        score = data.get("score", 0)
        critical = data.get("critical_count", 0)
        serious = data.get("serious_count", 0)

        deadline = datetime(2026, 4, 24)
        days_remaining = max(0, (deadline - datetime.now()).days)

        if score < 30:
            level = "CRITICAL"
            description = (
                "Your website has severe accessibility barriers. "
                "This level of non-compliance carries significant legal risk. "
                "Immediate professional remediation is strongly recommended."
            )
        elif score < 50:
            level = "HIGH"
            description = (
                "Your website has major accessibility issues that need urgent attention. "
                f"With {days_remaining} days until the ADA deadline, "
                "prioritize critical and serious violations immediately."
            )
        elif score < 80:
            level = "MEDIUM"
            description = (
                "Your website has some accessibility issues but has a reasonable foundation. "
                "Fix critical issues first and plan for remaining improvements."
            )
        else:
            level = "LOW"
            description = (
                "Your website is in good shape for accessibility compliance. "
                "Continue monitoring and fix any remaining issues."
            )

        return {
            "risk_level": level,
            "description": description,
            "days_until_deadline": days_remaining,
            "critical_violations": critical,
            "serious_violations": serious,
            "lawsuit_risk": "HIGH" if critical > 5 else "MEDIUM" if critical > 0 else "LOW",
        }

    def _get_recommendations(self, score, critical, serious):
        """Generate recommendations based on score."""
        recs = []

        if critical > 0:
            recs.append(
                "URGENT: Fix all critical violations immediately. "
                "Missing alt text and form labels are the most common basis for ADA lawsuits."
            )

        if serious > 0:
            recs.append(
                "Fix serious violations within 1-2 weeks. "
                "Page language and empty links significantly impact screen reader users."
            )

        if score < 70:
            recs.append(
                "Consider upgrading to a paid plan for AI-powered fix suggestions "
                "with specific code changes for your website."
            )

        recs.append(
            "Schedule weekly re-scans to catch new accessibility issues "
            "as your website content changes."
        )

        recs.append(
            "Add a 'Skip to Content' link and ARIA landmarks to improve "
            "keyboard navigation for all users."
        )

        return recs
