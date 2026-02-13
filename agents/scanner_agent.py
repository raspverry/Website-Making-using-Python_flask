"""
Scanner Agent - Crawls websites and detects WCAG 2.2 Level AA violations.

This agent uses PageGuard's built-in scanner engine and wraps it
with Claude's intelligence for deeper analysis.

Note: Scanner functions (run_scan, check_page, etc.) do NOT require
Flask app context - they are pure functions using requests + BeautifulSoup.
"""

import logging
from typing import Any, Optional

from agents.base import BaseAgent

logger = logging.getLogger(__name__)


def _import_scanner():
    """Import scanner module. Separated for clarity - no Flask context needed."""
    from app.scanner import run_scan, fetch_page, check_page, discover_pages
    return run_scan, fetch_page, check_page, discover_pages


class ScannerAgent(BaseAgent):
    name = "scanner"
    role = "WCAG Accessibility Scanner"
    system_prompt = """You are the Scanner Agent for PageGuard, an expert in WCAG 2.2 Level AA accessibility compliance.

Your role:
1. Crawl the given website URL and discover internal pages
2. Run WCAG accessibility checks on each page
3. Classify violations by severity (critical > serious > moderate > minor)
4. Return structured scan results

You have access to these tools:
- scan_website: Crawl and scan a website for WCAG violations
- scan_single_page: Scan a single page's HTML
- discover_links: Find internal links on a page

Always be thorough and report ALL violations found. Group results by page URL.
Report the compliance score (0-100) using the severity-weighted formula."""

    def get_tools(self) -> list[dict]:
        return [
            {
                "name": "scan_website",
                "description": "Crawl a website and scan all discovered pages for WCAG 2.2 Level AA accessibility violations. Returns violations grouped by page with severity ratings.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "The website URL to scan"},
                        "max_pages": {"type": "integer", "description": "Maximum pages to scan (default 5)", "default": 5},
                    },
                    "required": ["url"],
                },
            },
            {
                "name": "scan_single_page",
                "description": "Fetch and scan a single page for accessibility violations.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "The page URL to scan"},
                    },
                    "required": ["url"],
                },
            },
            {
                "name": "discover_links",
                "description": "Discover internal links on a page for further scanning.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "The page URL to find links on"},
                        "max_links": {"type": "integer", "description": "Maximum links to return", "default": 10},
                    },
                    "required": ["url"],
                },
            },
        ]

    def _handle_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "scan_website":
            return self._scan_website(tool_input["url"], tool_input.get("max_pages", 5))
        elif tool_name == "scan_single_page":
            return self._scan_single_page(tool_input["url"])
        elif tool_name == "discover_links":
            return self._discover_links(tool_input["url"], tool_input.get("max_links", 10))
        return {"error": f"Unknown tool: {tool_name}"}

    def _scan_website(self, url: str, max_pages: int) -> dict:
        """Run a full website scan using the PageGuard scanner engine."""
        run_scan, _, _, _ = _import_scanner()
        try:
            result = run_scan(url, max_pages=max_pages)
        except Exception as e:
            logger.error("[scanner] Failed to scan %s: %s", url, e)
            return {"error": f"Scan failed: {e}", "url": url}

        pages = []
        for page in result.pages:
            violations = []
            for v in page.violations:
                violations.append({
                    "rule_id": v.rule_id,
                    "rule_name": v.rule_name,
                    "severity": v.severity,
                    "wcag_criteria": v.wcag_criteria,
                    "description": v.description,
                    "element_html": (v.element_html or "")[:200],
                    "selector": v.selector or "",
                })
            pages.append({
                "url": page.url,
                "violations": violations,
                "violation_count": len(violations),
                "error": page.error or "",
            })

        return {
            "score": result.score,
            "total_violations": result.total_violations,
            "critical_count": result.critical_count,
            "serious_count": result.serious_count,
            "moderate_count": result.moderate_count,
            "minor_count": result.minor_count,
            "pages_scanned": len(result.pages),
            "pages": pages,
        }

    def _scan_single_page(self, url: str) -> dict:
        """Scan a single page."""
        _, fetch_page, check_page, _ = _import_scanner()
        try:
            html = fetch_page(url)
            result = check_page(url, html)
        except Exception as e:
            logger.error("[scanner] Failed to scan page %s: %s", url, e)
            return {"error": f"Page scan failed: {e}", "url": url}

        violations = []
        for v in result.violations:
            violations.append({
                "rule_id": v.rule_id,
                "rule_name": v.rule_name,
                "severity": v.severity,
                "wcag_criteria": v.wcag_criteria,
                "description": v.description,
                "element_html": (v.element_html or "")[:200],
            })
        return {"url": url, "violations": violations, "count": len(violations)}

    def _discover_links(self, url: str, max_links: int) -> dict:
        """Discover internal links."""
        _, fetch_page, _, discover_pages = _import_scanner()
        try:
            html = fetch_page(url)
            links = discover_pages(url, html, max_pages=max_links)
        except Exception as e:
            logger.error("[scanner] Failed to discover links on %s: %s", url, e)
            return {"error": f"Link discovery failed: {e}", "url": url}
        return {"url": url, "internal_links": links, "count": len(links)}
