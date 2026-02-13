"""
PageGuard AI Accessibility Agent

An intelligent agent that analyzes scan results and provides:
- Executive summary of accessibility status
- Prioritized remediation plan with effort estimates
- Trend analysis comparing scans over time
- Interactive Q&A about accessibility issues
"""

from flask import current_app


# Effort estimates (minutes) per rule fix
EFFORT_ESTIMATES = {
    "img-alt": {"min": 2, "max": 10, "label": "Quick fix"},
    "form-label": {"min": 5, "max": 15, "label": "Quick fix"},
    "html-lang": {"min": 1, "max": 2, "label": "Quick fix"},
    "page-title": {"min": 1, "max": 3, "label": "Quick fix"},
    "empty-link": {"min": 3, "max": 10, "label": "Quick fix"},
    "empty-button": {"min": 3, "max": 10, "label": "Quick fix"},
    "heading-order": {"min": 10, "max": 30, "label": "Moderate"},
    "skip-nav": {"min": 5, "max": 15, "label": "Quick fix"},
    "landmark-main": {"min": 5, "max": 20, "label": "Moderate"},
    "meta-viewport": {"min": 1, "max": 2, "label": "Quick fix"},
}

SEVERITY_WEIGHTS = {
    "critical": 4,
    "serious": 3,
    "moderate": 2,
    "minor": 1,
}


def analyze_scan(scan, violations):
    """Analyze a scan and produce structured insights."""
    # Group violations by rule
    by_rule = {}
    by_page = {}
    by_severity = {"critical": [], "serious": [], "moderate": [], "minor": []}

    for v in violations:
        by_rule.setdefault(v.rule_id, []).append(v)
        by_page.setdefault(v.page_url, []).append(v)
        by_severity.get(v.severity, []).append(v)

    # Calculate priority score for each rule group
    priorities = []
    total_effort_min = 0
    total_effort_max = 0

    for rule_id, rule_violations in by_rule.items():
        count = len(rule_violations)
        severity = rule_violations[0].severity
        weight = SEVERITY_WEIGHTS.get(severity, 1)
        effort = EFFORT_ESTIMATES.get(rule_id, {"min": 5, "max": 15, "label": "Moderate"})
        priority_score = weight * count

        effort_min = effort["min"] * count
        effort_max = effort["max"] * count
        total_effort_min += effort_min
        total_effort_max += effort_max

        priorities.append({
            "rule_id": rule_id,
            "rule_name": rule_violations[0].rule_name,
            "severity": severity,
            "count": count,
            "priority_score": priority_score,
            "effort_label": effort["label"],
            "effort_min": effort_min,
            "effort_max": effort_max,
            "pages": list(set(v.page_url for v in rule_violations if v.page_url)),
            "fix_suggestion": rule_violations[0].fix_suggestion or "",
        })

    priorities.sort(key=lambda x: x["priority_score"], reverse=True)

    # Determine risk level
    if scan.critical_count > 0:
        risk_level = "high"
        risk_label = "High Risk - Immediate action needed"
    elif scan.serious_count > 0:
        risk_level = "medium"
        risk_label = "Medium Risk - Fix soon"
    elif scan.moderate_count > 0:
        risk_level = "low"
        risk_label = "Low Risk - Minor improvements needed"
    else:
        risk_level = "minimal"
        risk_label = "Minimal Risk - Looking good!"

    # ADA compliance assessment
    if scan.score >= 90:
        compliance_status = "likely_compliant"
        compliance_label = "Likely Compliant"
    elif scan.score >= 70:
        compliance_status = "needs_work"
        compliance_label = "Needs Improvement"
    elif scan.score >= 50:
        compliance_status = "at_risk"
        compliance_label = "At Risk"
    else:
        compliance_status = "non_compliant"
        compliance_label = "Non-Compliant"

    return {
        "priorities": priorities,
        "by_severity": {k: len(v) for k, v in by_severity.items()},
        "by_page": {k: len(v) for k, v in by_page.items()},
        "pages_affected": len(by_page),
        "rules_violated": len(by_rule),
        "risk_level": risk_level,
        "risk_label": risk_label,
        "compliance_status": compliance_status,
        "compliance_label": compliance_label,
        "total_effort_min": total_effort_min,
        "total_effort_max": total_effort_max,
    }


def compare_scans(current_scan, previous_scan):
    """Compare two scans and return trend data."""
    if not previous_scan:
        return None

    score_diff = (current_scan.score or 0) - (previous_scan.score or 0)
    violations_diff = (current_scan.total_violations or 0) - (previous_scan.total_violations or 0)
    critical_diff = (current_scan.critical_count or 0) - (previous_scan.critical_count or 0)

    if score_diff > 0:
        trend = "improving"
        trend_label = f"Score improved by {score_diff} points"
    elif score_diff < 0:
        trend = "declining"
        trend_label = f"Score dropped by {abs(score_diff)} points"
    else:
        trend = "stable"
        trend_label = "Score unchanged"

    return {
        "trend": trend,
        "trend_label": trend_label,
        "score_diff": score_diff,
        "violations_diff": violations_diff,
        "critical_diff": critical_diff,
        "previous_score": previous_scan.score,
        "previous_violations": previous_scan.total_violations,
        "previous_date": previous_scan.completed_at or previous_scan.created_at,
    }


def generate_executive_summary(site, scan, analysis, trend=None):
    """Generate an executive summary using AI or rule-based fallback."""
    api_key = current_app.config.get("OPENAI_API_KEY", "")

    context = _build_summary_context(site, scan, analysis, trend)

    if api_key:
        try:
            return _ai_executive_summary(api_key, context)
        except Exception:
            pass

    return _fallback_executive_summary(site, scan, analysis, trend)


def generate_agent_response(question, site, scan, violations):
    """Answer a user's question about their accessibility issues using AI or fallback."""
    api_key = current_app.config.get("OPENAI_API_KEY", "")

    # Build violation context
    violation_summary = []
    for v in violations[:20]:  # Limit context size
        violation_summary.append(
            f"- [{v.severity}] {v.rule_name} on {v.page_url}: {v.description}"
        )
    violation_text = "\n".join(violation_summary) if violation_summary else "No violations found."

    if api_key:
        try:
            return _ai_answer_question(api_key, question, site, scan, violation_text)
        except Exception:
            pass

    return _fallback_answer(question, scan, violations)


def _build_summary_context(site, scan, analysis, trend):
    """Build a text context for AI summary generation."""
    parts = [
        f"Website: {site.url} ({site.name})",
        f"Compliance Score: {scan.score}/100",
        f"Pages Scanned: {scan.pages_scanned}",
        f"Total Violations: {scan.total_violations}",
        f"Critical: {scan.critical_count}, Serious: {scan.serious_count}, "
        f"Moderate: {scan.moderate_count}, Minor: {scan.minor_count}",
        f"Risk Level: {analysis['risk_label']}",
        f"ADA Compliance: {analysis['compliance_label']}",
        f"Estimated fix time: {analysis['total_effort_min']}-{analysis['total_effort_max']} minutes",
    ]

    if analysis["priorities"]:
        parts.append("\nTop issues:")
        for p in analysis["priorities"][:5]:
            parts.append(f"- {p['rule_name']} ({p['severity']}): {p['count']} instances")

    if trend:
        parts.append(f"\nTrend: {trend['trend_label']}")
        parts.append(f"Previous score: {trend['previous_score']}/100")

    return "\n".join(parts)


def _ai_executive_summary(api_key, context):
    """Generate executive summary using OpenAI."""
    import requests as req

    prompt = f"""You are an expert web accessibility consultant preparing a brief executive summary for a client.
Based on the following scan data, write a concise 3-4 paragraph executive summary covering:
1. Overall compliance status and risk level
2. Most critical issues requiring immediate attention
3. Recommended action plan with priorities
4. Estimated effort and timeline

Keep the tone professional but urgent given the ADA Title II deadline of April 24, 2026.
Write in plain English that a non-technical business owner can understand.

Scan Data:
{context}"""

    resp = req.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 600,
            "temperature": 0.4,
        },
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _fallback_executive_summary(site, scan, analysis, trend):
    """Generate a rule-based executive summary without AI."""
    score = scan.score or 0
    parts = []

    # Opening
    if score >= 90:
        parts.append(
            f"Your website {site.name} ({site.url}) scored {score}/100 on our accessibility audit. "
            f"This is an excellent score. Your site is well-positioned for ADA compliance."
        )
    elif score >= 70:
        parts.append(
            f"Your website {site.name} ({site.url}) scored {score}/100 on our accessibility audit. "
            f"While your site has a solid foundation, there are several issues that need attention "
            f"before the ADA Title II deadline on April 24, 2026."
        )
    elif score >= 50:
        parts.append(
            f"Your website {site.name} ({site.url}) scored {score}/100 on our accessibility audit. "
            f"This score indicates significant accessibility gaps that put your organization at risk. "
            f"With the ADA Title II deadline approaching on April 24, 2026, prompt action is recommended."
        )
    else:
        parts.append(
            f"Your website {site.name} ({site.url}) scored {score}/100 on our accessibility audit. "
            f"This is a critical score. Your site has major accessibility barriers that could expose "
            f"your organization to ADA lawsuits and fines up to $150,000 per violation. "
            f"Immediate remediation is strongly advised."
        )

    # Issues summary
    if scan.total_violations > 0:
        parts.append(
            f"\nWe found {scan.total_violations} accessibility violations across "
            f"{scan.pages_scanned} pages scanned. "
            f"Of these, {scan.critical_count} are critical, {scan.serious_count} are serious, "
            f"and {scan.moderate_count} are moderate."
        )

        if analysis["priorities"]:
            top = analysis["priorities"][0]
            parts.append(
                f"The most pressing issue is \"{top['rule_name']}\" with "
                f"{top['count']} instances found. This is rated as {top['severity']} severity."
            )

    # Effort estimate
    if analysis["total_effort_max"] > 0:
        hours_min = analysis["total_effort_min"] // 60
        hours_max = analysis["total_effort_max"] // 60
        if hours_max < 1:
            parts.append(
                f"\nEstimated remediation time: {analysis['total_effort_min']}-{analysis['total_effort_max']} minutes. "
                f"Most fixes are straightforward HTML changes."
            )
        else:
            parts.append(
                f"\nEstimated remediation time: approximately {max(1, hours_min)}-{max(1, hours_max)} hours. "
                f"We recommend starting with critical issues first."
            )

    # Trend
    if trend:
        if trend["trend"] == "improving":
            parts.append(f"\nGood news: your score has improved by {trend['score_diff']} points since the last scan.")
        elif trend["trend"] == "declining":
            parts.append(f"\nAlert: your score has dropped by {abs(trend['score_diff'])} points since the last scan. Review recent site changes.")

    return "\n".join(parts)


def _ai_answer_question(api_key, question, site, scan, violation_text):
    """Answer a user question using OpenAI."""
    import requests as req

    prompt = f"""You are PageGuard's AI accessibility assistant. A user has a question about their website's accessibility scan results.

Website: {site.url} ({site.name})
Score: {scan.score}/100
Total Violations: {scan.total_violations}

Violations found:
{violation_text}

User's question: {question}

Answer the question directly and concisely. If the question is about how to fix an issue, provide specific code examples.
If the question is not related to accessibility, politely redirect to accessibility topics.
Keep your answer under 200 words."""

    resp = req.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 400,
            "temperature": 0.4,
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _fallback_answer(question, scan, violations):
    """Provide a rule-based answer when AI is unavailable."""
    question_lower = question.lower()

    # Score-related questions
    if any(w in question_lower for w in ["score", "점수", "rating"]):
        return (
            f"Your current accessibility score is {scan.score}/100. "
            f"A score of 90+ is considered good for basic WCAG compliance. "
            f"You have {scan.total_violations} violations to fix: "
            f"{scan.critical_count} critical, {scan.serious_count} serious, "
            f"{scan.moderate_count} moderate."
        )

    # Fix-related questions
    if any(w in question_lower for w in ["fix", "how", "solve", "어떻게", "고치", "수정"]):
        if violations:
            top = violations[0]
            return (
                f"Start with the highest priority issue: {top.rule_name} ({top.severity}).\n\n"
                f"{top.fix_suggestion or top.description}\n\n"
                f"After fixing this, re-scan to check for improvements."
            )
        return "No violations found. Your site looks good!"

    # Priority / what first
    if any(w in question_lower for w in ["priority", "first", "important", "urgent", "우선", "먼저"]):
        critical = [v for v in violations if v.severity == "critical"]
        if critical:
            rules = set(v.rule_id for v in critical)
            return (
                f"Focus on {len(critical)} critical violations first: "
                f"{', '.join(rules)}. "
                f"These have the highest impact on users with disabilities "
                f"and carry the most legal risk."
            )
        return "You have no critical issues. Focus on serious violations next."

    # ADA / legal questions
    if any(w in question_lower for w in ["ada", "lawsuit", "legal", "fine", "법", "소송", "벌금"]):
        return (
            "The ADA Title II web accessibility deadline is April 24, 2026. "
            f"Your current score is {scan.score}/100. "
            f"Non-compliance can result in fines up to $75,000 for a first violation "
            f"and $150,000 for subsequent violations. "
            f"We recommend fixing all critical and serious issues before the deadline."
        )

    # Default response
    return (
        f"Your site has {scan.total_violations} accessibility violations "
        f"with a score of {scan.score}/100. "
        f"Critical issues: {scan.critical_count}, Serious: {scan.serious_count}. "
        f"Start by reviewing the prioritized remediation plan above, "
        f"and fix critical issues first. Feel free to ask specific questions "
        f"about any violation or how to fix it."
    )
