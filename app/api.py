from flask import Blueprint, jsonify
from app.models import Site, Scan, Violation

api_bp = Blueprint("api", __name__)


@api_bp.route("/sites/<site_uid>/latest-scan")
def latest_scan(site_uid):
    site = Site.query.filter_by(uid=site_uid).first()
    if not site:
        return jsonify({"error": "Site not found"}), 404

    scan = site.latest_scan()
    if not scan:
        return jsonify({"error": "No scans yet"}), 404

    violations = scan.violations.all()

    return jsonify({
        "site": {"url": site.url, "name": site.name},
        "scan": {
            "score": scan.score,
            "status": scan.status,
            "pages_scanned": scan.pages_scanned,
            "total_violations": scan.total_violations,
            "critical": scan.critical_count,
            "serious": scan.serious_count,
            "moderate": scan.moderate_count,
            "minor": scan.minor_count,
            "scanned_at": scan.created_at.isoformat() if scan.created_at else None,
        },
        "violations": [
            {
                "rule_id": v.rule_id,
                "rule_name": v.rule_name,
                "severity": v.severity,
                "wcag": v.wcag_criteria,
                "description": v.description,
                "element": v.element_html,
                "page_url": v.page_url,
                "fix": v.fix_suggestion,
            }
            for v in violations
        ],
    })
