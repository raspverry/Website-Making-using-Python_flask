"""
Report generation service for PageGuard.
Generates PDF and text compliance reports from scan results.
"""

import io
import logging
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable,
)

logger = logging.getLogger(__name__)

# Color scheme
BRAND_BLUE = colors.HexColor("#2563EB")
BRAND_RED = colors.HexColor("#DC2626")
BRAND_GREEN = colors.HexColor("#16A34A")
SEVERITY_COLORS = {
    "critical": colors.HexColor("#DC2626"),
    "serious": colors.HexColor("#EA580C"),
    "moderate": colors.HexColor("#CA8A04"),
    "minor": colors.HexColor("#6B7280"),
}


def _get_styles():
    """Custom paragraph styles for the PDF report."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=24,
        textColor=BRAND_BLUE,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        "SectionHead",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=BRAND_BLUE,
        spaceBefore=16,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        "ViolationTitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.black,
        spaceBefore=10,
        spaceAfter=2,
        leading=14,
    ))
    styles.add(ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.grey,
    ))
    styles.add(ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontSize=7,
        textColor=colors.grey,
        spaceBefore=12,
    ))
    return styles


def generate_pdf_report(site_url: str, scan_data: dict, violations: list) -> bytes:
    """Generate a professional PDF compliance report. Returns PDF bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )
    styles = _get_styles()
    story = []

    # --- Header ---
    story.append(Paragraph("PageGuard", styles["ReportTitle"]))
    story.append(Paragraph("Web Accessibility Compliance Report", styles["Heading3"]))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=2, color=BRAND_BLUE))
    story.append(Spacer(1, 12))

    # --- Summary table ---
    scan_date = scan_data.get("completed_at") or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    score = scan_data.get("score", 0)
    score_color = BRAND_GREEN if score >= 80 else (colors.HexColor("#CA8A04") if score >= 50 else BRAND_RED)

    summary_data = [
        ["Website", site_url],
        ["Scan Date", str(scan_date)],
        ["Compliance Score", f"{score} / 100"],
        ["Pages Scanned", str(scan_data.get("pages_scanned", 0))],
        ["Total Violations", str(scan_data.get("total_violations", 0))],
        ["Critical", str(scan_data.get("critical_count", 0))],
        ["Serious", str(scan_data.get("serious_count", 0))],
        ["Moderate", str(scan_data.get("moderate_count", 0))],
        ["Minor", str(scan_data.get("minor_count", 0))],
    ]

    summary_table = Table(summary_data, colWidths=[2.2 * inch, 4 * inch])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F3F4F6")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#374151")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (0, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#FAFAFA")]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))

    # --- Score assessment ---
    if score >= 80:
        assessment = "Your website shows good accessibility compliance. Address the remaining issues to achieve full compliance."
    elif score >= 50:
        assessment = "Your website has significant accessibility gaps. Prioritize fixing critical and serious violations before the ADA deadline."
    else:
        assessment = "Your website has major accessibility failures. Immediate action is required to avoid ADA non-compliance penalties."

    story.append(Paragraph("Assessment", styles["SectionHead"]))
    story.append(Paragraph(assessment, styles["Normal"]))

    # --- ADA Deadline Warning ---
    story.append(Spacer(1, 12))
    warning_data = [["ADA Title II Compliance Deadline: April 24, 2026\n"
                      "Non-compliance penalties: up to $150,000 per violation"]]
    warning_table = Table(warning_data, colWidths=[6.2 * inch])
    warning_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FEF2F2")),
        ("TEXTCOLOR", (0, 0), (-1, -1), BRAND_RED),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("BOX", (0, 0), (-1, -1), 1, BRAND_RED),
    ]))
    story.append(warning_table)

    # --- Violations Detail ---
    if violations:
        story.append(Paragraph("Violations Detail", styles["SectionHead"]))

        for i, v in enumerate(violations, 1):
            severity = v.get("severity", "unknown")
            sev_color = SEVERITY_COLORS.get(severity, colors.grey)

            # Violation header with severity badge
            story.append(Paragraph(
                f'<font color="{sev_color.hexval()}">[{severity.upper()}]</font> '
                f'<b>{v.get("rule_name", "Unknown")}</b> '
                f'<font color="#6B7280">(WCAG {v.get("wcag_criteria", "N/A")})</font>',
                styles["ViolationTitle"],
            ))

            # Details
            desc = v.get("description", "")
            page_url = v.get("page_url", "")
            element = v.get("element_html", "")[:120]
            fix = v.get("fix_suggestion", "")[:300]

            detail_parts = [f"<b>Page:</b> {page_url}"] if page_url else []
            if desc:
                detail_parts.append(f"<b>Issue:</b> {desc}")
            if element:
                safe_element = element.replace("<", "&lt;").replace(">", "&gt;")
                detail_parts.append(f"<b>Element:</b> <font face='Courier' size='8'>{safe_element}</font>")
            if fix:
                detail_parts.append(f"<b>Fix:</b> {fix}")

            for part in detail_parts:
                story.append(Paragraph(part, styles["Normal"]))

            story.append(Spacer(1, 4))

    # --- Disclaimer ---
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(Paragraph(
        "DISCLAIMER: This report is generated by automated accessibility testing and checks for common "
        "WCAG 2.2 Level AA violations. Automated tools can only detect approximately 30% of accessibility "
        "issues. This report should NOT be used as legal evidence of compliance. We recommend combining "
        "automated testing with manual accessibility audits. PageGuard is not a law firm and does not "
        "provide legal advice. Consult an accessibility expert and legal counsel for full compliance.",
        styles["Disclaimer"],
    ))
    story.append(Paragraph(
        f"Report generated by PageGuard (https://pageguard.dev) on "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        styles["Small"],
    ))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    logger.info("Generated PDF report for %s (%d bytes)", site_url, len(pdf_bytes))
    return pdf_bytes


def generate_text_report(site_url: str, scan_data: dict, violations: list) -> str:
    """Generate a plain text compliance report."""
    lines = [
        "=" * 60,
        "PageGuard Web Accessibility Compliance Report",
        "=" * 60,
        f"Website: {site_url}",
        f"Scan Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"Compliance Score: {scan_data.get('score', 'N/A')}/100",
        f"Pages Scanned: {scan_data.get('pages_scanned', 0)}",
        f"Total Violations: {scan_data.get('total_violations', 0)}",
        "",
        "Violation Breakdown:",
        f"  Critical: {scan_data.get('critical_count', 0)}",
        f"  Serious:  {scan_data.get('serious_count', 0)}",
        f"  Moderate: {scan_data.get('moderate_count', 0)}",
        f"  Minor:    {scan_data.get('minor_count', 0)}",
        "",
        "-" * 60,
        "VIOLATIONS DETAIL",
        "-" * 60,
    ]

    for i, v in enumerate(violations, 1):
        lines.extend([
            f"\n{i}. [{v.get('severity', 'unknown').upper()}] {v.get('rule_name', 'Unknown Rule')}",
            f"   WCAG: {v.get('wcag_criteria', 'N/A')}",
            f"   Page: {v.get('page_url', 'N/A')}",
            f"   Description: {v.get('description', '')}",
            f"   Element: {v.get('element_html', 'N/A')[:100]}",
            f"   Fix: {v.get('fix_suggestion', 'See WCAG guidelines')[:200]}",
        ])

    lines.extend([
        "",
        "=" * 60,
        "DISCLAIMER: This report is generated by automated testing.",
        "It should NOT be used as legal evidence of full compliance.",
        "Consult an accessibility expert for a comprehensive audit.",
        "",
        "ADA Title II Compliance Deadline: April 24, 2026",
        "Non-compliance penalties: up to $150,000 per violation",
        "Report generated by PageGuard (https://pageguard.dev)",
        "=" * 60,
    ])

    return "\n".join(lines)
