from datetime import datetime, timezone
from urllib.parse import urlparse

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user

from app import db
from app.models import Site, Scan, Violation
from app.scanner import run_scan
from app.ai_suggestions import generate_fix

dashboard_bp = Blueprint("dashboard", __name__)


def normalize_url(url):
    """Ensure URL has a scheme and is valid."""
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    if not parsed.netloc:
        return None
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")


@dashboard_bp.route("/")
@login_required
def index():
    sites = current_user.sites.order_by(Site.created_at.desc()).all()
    return render_template("dashboard/index.html", sites=sites)


@dashboard_bp.route("/sites/add", methods=["GET", "POST"])
@login_required
def add_site():
    if not current_user.can_add_site():
        flash("You've reached your site limit. Upgrade your plan to add more.", "error")
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        url = request.form.get("url", "").strip()
        name = request.form.get("name", "").strip()

        normalized = normalize_url(url)
        if not normalized:
            flash("Please enter a valid URL.", "error")
            return render_template("dashboard/add_site.html", url=url, name=name)

        if not name:
            name = urlparse(normalized).netloc

        # Check for duplicate
        existing = Site.query.filter_by(user_id=current_user.id, url=normalized).first()
        if existing:
            flash("You've already added this website.", "error")
            return render_template("dashboard/add_site.html", url=url, name=name)

        site = Site(url=normalized, name=name, user_id=current_user.id)
        db.session.add(site)
        db.session.commit()

        flash(f"Website added! Running your first scan...", "success")
        return redirect(url_for("dashboard.run_site_scan", site_uid=site.uid))

    return render_template("dashboard/add_site.html")


@dashboard_bp.route("/sites/<site_uid>")
@login_required
def site_detail(site_uid):
    site = Site.query.filter_by(uid=site_uid, user_id=current_user.id).first_or_404()
    scans = site.scans.order_by(Scan.created_at.desc()).limit(10).all()
    latest = site.latest_scan()
    return render_template("dashboard/site_detail.html", site=site, scans=scans, latest=latest)


@dashboard_bp.route("/sites/<site_uid>/scan", methods=["GET", "POST"])
@login_required
def run_site_scan(site_uid):
    site = Site.query.filter_by(uid=site_uid, user_id=current_user.id).first_or_404()

    limits = current_user.get_plan_limits()
    max_pages = limits["max_pages"]

    # Create scan record
    scan = Scan(site_id=site.id, status="running")
    db.session.add(scan)
    db.session.commit()

    try:
        scan_result = run_scan(site.url, max_pages=max_pages)

        scan.status = "completed"
        scan.score = scan_result.score
        scan.pages_scanned = len(scan_result.pages)
        scan.total_violations = scan_result.total_violations
        scan.critical_count = scan_result.critical_count
        scan.serious_count = scan_result.serious_count
        scan.moderate_count = scan_result.moderate_count
        scan.minor_count = scan_result.minor_count
        scan.completed_at = datetime.now(timezone.utc)

        # Save violations
        for page in scan_result.pages:
            for v in page.violations:
                fix_text = ""
                if current_user.has_ai_fixes():
                    fix_text = generate_fix(v.rule_id, v.description, v.element_html)
                else:
                    from app.ai_suggestions import RULE_FIXES
                    rule_fix = RULE_FIXES.get(v.rule_id, {})
                    fix_text = rule_fix.get("fix_template", "")

                violation = Violation(
                    scan_id=scan.id,
                    rule_id=v.rule_id,
                    rule_name=v.rule_name,
                    severity=v.severity,
                    wcag_criteria=v.wcag_criteria,
                    description=v.description,
                    element_html=v.element_html,
                    page_url=page.url,
                    fix_suggestion=fix_text,
                    selector=v.selector,
                )
                db.session.add(violation)

        # Update site
        site.compliance_score = scan_result.score
        site.last_scan_at = datetime.now(timezone.utc)

        db.session.commit()

    except Exception as e:
        scan.status = "failed"
        db.session.commit()
        flash(f"Scan failed: {str(e)}", "error")
        return redirect(url_for("dashboard.site_detail", site_uid=site.uid))

    return redirect(url_for("dashboard.scan_results", scan_uid=scan.uid))


@dashboard_bp.route("/scans/<scan_uid>")
@login_required
def scan_results(scan_uid):
    scan = Scan.query.filter_by(uid=scan_uid).first_or_404()
    site = Site.query.filter_by(id=scan.site_id, user_id=current_user.id).first_or_404()

    severity_filter = request.args.get("severity", "all")
    if severity_filter != "all":
        violations = scan.violations.filter_by(severity=severity_filter).all()
    else:
        violations = scan.violations.order_by(
            db.case(
                (Violation.severity == "critical", 0),
                (Violation.severity == "serious", 1),
                (Violation.severity == "moderate", 2),
                else_=3,
            )
        ).all()

    return render_template(
        "dashboard/scan_results.html",
        scan=scan,
        site=site,
        violations=violations,
        severity_filter=severity_filter,
    )


@dashboard_bp.route("/sites/<site_uid>/delete", methods=["POST"])
@login_required
def delete_site(site_uid):
    site = Site.query.filter_by(uid=site_uid, user_id=current_user.id).first_or_404()
    db.session.delete(site)
    db.session.commit()
    flash(f"Site removed.", "info")
    return redirect(url_for("dashboard.index"))
