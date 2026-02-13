"""
Agent routes - AI accessibility audit agent interface.
Provides executive summaries, remediation plans, trend analysis, and Q&A.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user

from app.models import Site, Scan, Violation
from app.agent import analyze_scan, compare_scans, generate_executive_summary, generate_agent_response

agent_bp = Blueprint("agent", __name__)


@agent_bp.route("/sites/<site_uid>/agent")
@login_required
def audit(site_uid):
    """AI agent audit page for a site."""
    site = Site.query.filter_by(uid=site_uid, user_id=current_user.id).first_or_404()
    latest = site.latest_scan()

    if not latest or latest.status != "completed":
        flash("Run a scan first to use the AI agent.", "info")
        return redirect(url_for("dashboard.site_detail", site_uid=site.uid))

    # Get violations for the latest scan
    violations = latest.violations.order_by(Violation.severity).all()

    # Analyze
    analysis = analyze_scan(latest, violations)

    # Compare with previous scan
    scans = site.scans.filter(Scan.status == "completed").order_by(Scan.created_at.desc()).limit(2).all()
    previous = scans[1] if len(scans) > 1 else None
    trend = compare_scans(latest, previous)

    # Generate executive summary
    summary = generate_executive_summary(site, latest, analysis, trend)

    # Scan history for chart (last 10 scans)
    history = (
        site.scans.filter(Scan.status == "completed")
        .order_by(Scan.created_at.asc())
        .limit(10)
        .all()
    )
    history_data = [
        {"date": (s.completed_at or s.created_at).strftime("%b %d"), "score": s.score or 0}
        for s in history
    ]

    return render_template(
        "dashboard/agent.html",
        site=site,
        scan=latest,
        violations=violations,
        analysis=analysis,
        trend=trend,
        summary=summary,
        history_data=history_data,
    )


@agent_bp.route("/sites/<site_uid>/agent/ask", methods=["POST"])
@login_required
def ask(site_uid):
    """Handle Q&A with the AI agent."""
    site = Site.query.filter_by(uid=site_uid, user_id=current_user.id).first_or_404()
    latest = site.latest_scan()

    if not latest:
        return jsonify({"error": "No scan data available"}), 400

    question = request.form.get("question", "").strip()
    if not question:
        return jsonify({"error": "Please enter a question"}), 400

    violations = latest.violations.all()
    answer = generate_agent_response(question, site, latest, violations)

    return jsonify({"answer": answer})
