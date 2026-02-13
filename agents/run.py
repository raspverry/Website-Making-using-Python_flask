#!/usr/bin/env python3
"""
PageGuard Multi-Agent Runner

Run a full accessibility audit using the multi-agent team:
  - Scanner Agent: Finds WCAG violations
  - Fix Agent: Generates code fixes
  - Report Agent: Creates compliance report
  - Orchestrator: Coordinates the team

Usage:
    # Full audit (direct orchestration, no extra API call)
    python -m agents.run https://example.com

    # With max pages
    python -m agents.run https://example.com --max-pages 10

    # AI-orchestrated audit (uses Claude to coordinate agents)
    python -m agents.run https://example.com --ai-orchestrate

    # Run a single agent
    python -m agents.run https://example.com --agent scanner
    python -m agents.run https://example.com --agent fixer
    python -m agents.run https://example.com --agent reporter

Environment:
    ANTHROPIC_API_KEY - Required for AI-orchestrated mode and agent delegation
"""

import argparse
import json
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def main():
    parser = argparse.ArgumentParser(
        description="PageGuard Multi-Agent Accessibility Audit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m agents.run https://example.com
  python -m agents.run https://example.com --max-pages 10
  python -m agents.run https://example.com --ai-orchestrate
  python -m agents.run https://example.com --agent scanner
        """,
    )
    parser.add_argument("url", help="Website URL to scan")
    parser.add_argument("--max-pages", type=int, default=5, help="Maximum pages to scan (default: 5)")
    parser.add_argument("--ai-orchestrate", action="store_true", help="Use AI to orchestrate agents (requires ANTHROPIC_API_KEY)")
    parser.add_argument("--agent", choices=["scanner", "fixer", "reporter"], help="Run a single agent")
    parser.add_argument("--output", "-o", help="Save results to JSON file")
    parser.add_argument("--api-key", help="Anthropic API key (or set ANTHROPIC_API_KEY env var)")

    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY", "")

    # Ensure URL has scheme
    url = args.url
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    if args.agent:
        # Run a single agent
        run_single_agent(args.agent, url, args.max_pages, api_key)
    elif args.ai_orchestrate:
        # AI-orchestrated multi-agent audit
        if not api_key:
            print("Error: ANTHROPIC_API_KEY required for --ai-orchestrate mode")
            print("Set it with: export ANTHROPIC_API_KEY=your-key")
            sys.exit(1)
        run_ai_orchestrated(url, args.max_pages, api_key, args.output)
    else:
        # Direct orchestration (default - works without API key for scanning)
        run_direct_audit(url, args.max_pages, api_key, args.output)


def run_direct_audit(url, max_pages, api_key, output_file):
    """Run direct multi-agent audit without AI orchestration."""
    from backend.services.scanner import run_scan
    from backend.services.ai_service import RULE_FIXES
    from agents.report_agent import ReportAgent

    print(f"\n{'='*60}")
    print(f"  PAGEGUARD MULTI-AGENT ACCESSIBILITY AUDIT")
    print(f"  URL: {url}")
    print(f"  Max Pages: {max_pages}")
    print(f"{'='*60}")

    # Step 1: Scanner
    print(f"\n[Step 1/3] Scanner Agent scanning {url}...")
    try:
        scan_result = run_scan(url, max_pages=max_pages)
    except Exception as e:
        print(f"\n  Error: Failed to scan {url}: {e}")
        sys.exit(1)

    print(f"  Score: {scan_result.score}/100")
    print(f"  Pages scanned: {len(scan_result.pages)}")
    print(f"  Violations: {scan_result.total_violations}")
    print(f"    Critical: {scan_result.critical_count}")
    print(f"    Serious:  {scan_result.serious_count}")
    print(f"    Moderate: {scan_result.moderate_count}")
    print(f"    Minor:    {scan_result.minor_count}")

    # Step 2: Fix Agent
    print(f"\n[Step 2/3] Fix Agent generating remediation suggestions...")
    fixes = []
    for page in scan_result.pages:
        for v in page.violations:
            rule_fix = RULE_FIXES.get(v.rule_id, {})
            fixes.append({
                "rule_id": v.rule_id,
                "rule_name": v.rule_name,
                "severity": v.severity,
                "page_url": page.url,
                "element": v.element_html[:100] if v.element_html else "",
                "explanation": rule_fix.get("explanation", v.description),
                "fix": rule_fix.get("fix_template", "Review WCAG 2.2 guidelines."),
            })

    # Group fixes by rule
    by_rule = {}
    for f in fixes:
        by_rule.setdefault(f["rule_id"], []).append(f)

    for rule_id, group in by_rule.items():
        print(f"  [{group[0]['severity'].upper()}] {group[0]['rule_name']}: {len(group)} instance(s)")

    # Step 3: Report
    print(f"\n[Step 3/3] Report Agent creating compliance report...")

    violations_summary = []
    for rule_id, group in by_rule.items():
        violations_summary.append({
            "rule_id": rule_id,
            "rule_name": group[0]["rule_name"],
            "severity": group[0]["severity"],
            "count": len(group),
        })

    # Use Report Agent tool directly
    reporter = ReportAgent(api_key=api_key)
    report_data = {
        "url": url,
        "score": scan_result.score,
        "total_violations": scan_result.total_violations,
        "critical_count": scan_result.critical_count,
        "serious_count": scan_result.serious_count,
        "moderate_count": scan_result.moderate_count,
        "minor_count": scan_result.minor_count,
        "pages_scanned": len(scan_result.pages),
        "violations_summary": violations_summary,
        "total_effort_minutes": sum(
            {"img-alt": 5, "form-label": 10, "html-lang": 1, "page-title": 2,
             "empty-link": 5, "empty-button": 5, "heading-order": 15,
             "skip-nav": 5, "landmark-main": 10, "meta-viewport": 1}.get(f["rule_id"], 10)
            for f in fixes
        ),
    }
    report = reporter._generate_report(report_data)

    print(f"\n{'='*60}")
    print(f"  AUDIT RESULTS")
    print(f"{'='*60}")
    print(f"\n  Website:     {url}")
    print(f"  Score:       {scan_result.score}/100")
    print(f"  Status:      {report['summary']['compliance_status']}")
    print(f"  Risk:        {report['risk_assessment']['risk_level']}")
    print(f"  Deadline:    {report['risk_assessment']['days_remaining']} days until ADA deadline")
    print(f"  Fix effort:  {report['remediation']['estimated_effort_display']}")
    print(f"\n  Recommendations:")
    for i, rec in enumerate(report["recommendations"], 1):
        print(f"    {i}. {rec}")
    print(f"\n{'='*60}\n")

    # Save results
    results = {
        "url": url,
        "score": scan_result.score,
        "scan": {
            "total_violations": scan_result.total_violations,
            "critical": scan_result.critical_count,
            "serious": scan_result.serious_count,
            "moderate": scan_result.moderate_count,
            "minor": scan_result.minor_count,
            "pages_scanned": len(scan_result.pages),
        },
        "fixes": fixes,
        "report": report,
    }

    if output_file:
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        print(f"Results saved to {output_file}")

    return results


def run_ai_orchestrated(url, max_pages, api_key, output_file):
    """Run AI-orchestrated multi-agent audit."""
    from agents.orchestrator import OrchestratorAgent

    orchestrator = OrchestratorAgent(api_key=api_key)
    result = orchestrator.run(
        task=f"""Run a complete accessibility audit on {url}:
1. First, delegate to the Scanner Agent to scan the website (max {max_pages} pages)
2. Then, delegate to the Fix Agent to generate fixes for all violations
3. Finally, delegate to the Report Agent to create a compliance report

Present the final results clearly with score, key violations, fixes, and risk assessment."""
    )

    print(f"\n{'='*60}")
    print(f"  AI-ORCHESTRATED AUDIT RESULTS")
    print(f"{'='*60}")
    print(result["text"])

    if output_file:
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to {output_file}")


def run_single_agent(agent_name, url, max_pages, api_key):
    """Run a single agent."""
    if not api_key:
        print(f"Error: ANTHROPIC_API_KEY required for running individual agents")
        sys.exit(1)

    if agent_name == "scanner":
        from agents.scanner_agent import ScannerAgent
        agent = ScannerAgent(api_key=api_key)
        result = agent.run(task=f"Scan {url} for WCAG 2.2 Level AA violations. Max {max_pages} pages.")
    elif agent_name == "fixer":
        from agents.fix_agent import FixAgent
        agent = FixAgent(api_key=api_key)
        result = agent.run(task=f"Generate accessibility fixes for the website {url}.")
    elif agent_name == "reporter":
        from agents.report_agent import ReportAgent
        agent = ReportAgent(api_key=api_key)
        result = agent.run(task=f"Create an accessibility compliance report for {url}.")
    else:
        print(f"Unknown agent: {agent_name}")
        sys.exit(1)

    print(f"\n[{agent_name.upper()} AGENT RESULT]")
    print(result["text"])


if __name__ == "__main__":
    main()
