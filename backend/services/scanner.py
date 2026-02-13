"""
PageGuard Accessibility Scanner Engine

Scans HTML pages for WCAG 2.2 Level AA violations using BeautifulSoup.
Checks the 10 most common accessibility issues that affect 95%+ of websites.
"""

import logging
import re
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, field

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class ViolationResult:
    rule_id: str
    rule_name: str
    severity: str  # critical, serious, moderate, minor
    wcag_criteria: str
    description: str
    element_html: str = ""
    selector: str = ""


@dataclass
class PageResult:
    url: str
    violations: list = field(default_factory=list)
    error: str = ""


@dataclass
class ScanResult:
    pages: list = field(default_factory=list)
    score: int = 100
    total_violations: int = 0
    critical_count: int = 0
    serious_count: int = 0
    moderate_count: int = 0
    minor_count: int = 0


def fetch_page(url, timeout=30):
    """Fetch a page and return its HTML content."""
    headers = {
        "User-Agent": "PageGuard Accessibility Scanner/1.0 (+https://pageguard.dev/bot)"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        if "text/html" not in content_type and "text/xhtml" not in content_type:
            raise ValueError(f"Not an HTML page (content-type: {content_type})")
        return resp.text
    except requests.exceptions.Timeout:
        raise ConnectionError(f"Timeout after {timeout}s fetching {url}")
    except requests.exceptions.SSLError as e:
        raise ConnectionError(f"SSL error for {url}: {e}")
    except requests.exceptions.ConnectionError as e:
        raise ConnectionError(f"Cannot connect to {url}: {e}")
    except requests.exceptions.HTTPError as e:
        raise ConnectionError(f"HTTP {e.response.status_code} for {url}")


def discover_pages(base_url, html, max_pages=5):
    """Find internal links on the page to crawl."""
    soup = BeautifulSoup(html, "lxml")
    parsed_base = urlparse(base_url)
    pages = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)

        # Only same domain, no fragments, no query params for simplicity
        if parsed.netloc == parsed_base.netloc and parsed.scheme in ("http", "https"):
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if clean_url != base_url:
                pages.add(clean_url)

        if len(pages) >= max_pages - 1:  # -1 because base_url is already included
            break

    return list(pages)


def check_page(url, html):
    """Run all WCAG checks on a single page. Returns a PageResult."""
    soup = BeautifulSoup(html, "lxml")
    violations = []

    # 1. Missing alt text on images (WCAG 1.1.1)
    for img in soup.find_all("img"):
        alt = img.get("alt")
        if alt is None:
            violations.append(ViolationResult(
                rule_id="img-alt",
                rule_name="Images must have alt text",
                severity="critical",
                wcag_criteria="1.1.1",
                description="Image is missing an alt attribute. Screen readers cannot describe this image to visually impaired users.",
                element_html=str(img)[:200],
                selector=_build_selector(img),
            ))

    # 2. Missing form labels (WCAG 1.3.1)
    for inp in soup.find_all(["input", "select", "textarea"]):
        if inp.get("type") in ("hidden", "submit", "button", "reset", "image"):
            continue
        inp_id = inp.get("id")
        has_label = False
        if inp_id:
            has_label = soup.find("label", attrs={"for": inp_id}) is not None
        if not has_label:
            has_label = inp.find_parent("label") is not None
        if not has_label and not inp.get("aria-label") and not inp.get("aria-labelledby"):
            violations.append(ViolationResult(
                rule_id="form-label",
                rule_name="Form elements must have labels",
                severity="critical",
                wcag_criteria="1.3.1",
                description="Form input is missing an associated label. Users relying on screen readers won't know what this field is for.",
                element_html=str(inp)[:200],
                selector=_build_selector(inp),
            ))

    # 3. Missing page language (WCAG 3.1.1)
    html_tag = soup.find("html")
    if html_tag and not html_tag.get("lang"):
        violations.append(ViolationResult(
            rule_id="html-lang",
            rule_name="Page must have a language attribute",
            severity="serious",
            wcag_criteria="3.1.1",
            description="The <html> element is missing a lang attribute. Screen readers need this to pronounce content correctly.",
            element_html='<html>' if html_tag else '',
            selector="html",
        ))

    # 4. Missing document title (WCAG 2.4.2)
    title = soup.find("title")
    if not title or not title.get_text(strip=True):
        violations.append(ViolationResult(
            rule_id="page-title",
            rule_name="Page must have a descriptive title",
            severity="serious",
            wcag_criteria="2.4.2",
            description="The page is missing a <title> element. This helps users understand the page purpose and is used by screen readers.",
            element_html="<title></title>",
            selector="head > title",
        ))

    # 5. Empty links (WCAG 2.4.4)
    for a_tag in soup.find_all("a"):
        text = a_tag.get_text(strip=True)
        has_img_alt = any(img.get("alt") for img in a_tag.find_all("img") if img.get("alt"))
        aria = a_tag.get("aria-label") or a_tag.get("aria-labelledby")
        if not text and not has_img_alt and not aria:
            violations.append(ViolationResult(
                rule_id="empty-link",
                rule_name="Links must have discernible text",
                severity="serious",
                wcag_criteria="2.4.4",
                description="Link has no text content, alt text on images, or aria-label. Users won't know where this link goes.",
                element_html=str(a_tag)[:200],
                selector=_build_selector(a_tag),
            ))

    # 6. Empty buttons (WCAG 4.1.2)
    for btn in soup.find_all("button"):
        text = btn.get_text(strip=True)
        aria = btn.get("aria-label") or btn.get("aria-labelledby")
        if not text and not aria:
            violations.append(ViolationResult(
                rule_id="empty-button",
                rule_name="Buttons must have discernible text",
                severity="serious",
                wcag_criteria="4.1.2",
                description="Button has no text or aria-label. Screen reader users won't know what this button does.",
                element_html=str(btn)[:200],
                selector=_build_selector(btn),
            ))

    # 7. Missing heading structure (WCAG 1.3.1)
    headings = soup.find_all(re.compile(r'^h[1-6]$'))
    if not headings:
        violations.append(ViolationResult(
            rule_id="heading-order",
            rule_name="Page should have a heading structure",
            severity="moderate",
            wcag_criteria="1.3.1",
            description="No headings found on the page. Headings help users navigate and understand content structure.",
            element_html="",
            selector="",
        ))
    else:
        prev_level = 0
        for h in headings:
            level = int(h.name[1])
            if prev_level > 0 and level > prev_level + 1:
                violations.append(ViolationResult(
                    rule_id="heading-order",
                    rule_name="Heading levels should not skip",
                    severity="moderate",
                    wcag_criteria="1.3.1",
                    description=f"Heading jumps from <h{prev_level}> to <h{level}>. This breaks the logical heading hierarchy.",
                    element_html=str(h)[:200],
                    selector=_build_selector(h),
                ))
            prev_level = level

    # 8. Missing skip navigation (WCAG 2.4.1)
    first_link = soup.find("a")
    has_skip = False
    if first_link:
        href = first_link.get("href", "")
        text = first_link.get_text(strip=True).lower()
        if href.startswith("#") and ("skip" in text or "main" in text or "content" in text):
            has_skip = True
    # Also check for any "skip" link in first 5 links
    if not has_skip:
        for a_tag in soup.find_all("a")[:5]:
            href = a_tag.get("href", "")
            text = a_tag.get_text(strip=True).lower()
            if href.startswith("#") and ("skip" in text or "main" in text):
                has_skip = True
                break
    if not has_skip and headings:  # Only flag if page has some structure
        violations.append(ViolationResult(
            rule_id="skip-nav",
            rule_name="Page should have a skip navigation link",
            severity="moderate",
            wcag_criteria="2.4.1",
            description="No 'skip to content' link found. Keyboard users must tab through all navigation links to reach main content.",
            element_html="",
            selector="body > a:first-child",
        ))

    # 9. Missing ARIA roles on landmarks (WCAG 4.1.2)
    has_main = soup.find("main") or soup.find(attrs={"role": "main"})
    if not has_main and len(str(soup)) > 1000:  # Only flag for substantial pages
        violations.append(ViolationResult(
            rule_id="landmark-main",
            rule_name="Page should have a main landmark",
            severity="moderate",
            wcag_criteria="4.1.2",
            description="No <main> element or role='main' found. Screen reader users need landmarks to navigate page sections.",
            element_html="",
            selector="body",
        ))

    # 10. Missing meta viewport (mobile accessibility)
    meta_viewport = soup.find("meta", attrs={"name": "viewport"})
    if meta_viewport:
        content = meta_viewport.get("content", "")
        if "maximum-scale=1" in content.replace(" ", "") or "user-scalable=no" in content.replace(" ", ""):
            violations.append(ViolationResult(
                rule_id="meta-viewport",
                rule_name="Zooming should not be disabled",
                severity="critical",
                wcag_criteria="1.4.4",
                description="Viewport meta tag disables user zooming. Users with low vision need to zoom in to read content.",
                element_html=str(meta_viewport)[:200],
                selector='meta[name="viewport"]',
            ))

    # 11. Color contrast detection (WCAG 1.4.3)
    # Static analysis can detect inline styles with low-contrast patterns
    for el in soup.find_all(style=True):
        style_str = el.get("style", "")
        colors_found = re.findall(r'color\s*:\s*(#[0-9a-fA-F]{3,6}|(?:rgb|rgba)\([^)]+\)|white|black|gray|grey)', style_str)
        bg_found = re.findall(r'background(?:-color)?\s*:\s*(#[0-9a-fA-F]{3,6}|(?:rgb|rgba)\([^)]+\)|white|black|gray|grey)', style_str)
        if colors_found and bg_found:
            fg = colors_found[0].lower()
            bg = bg_found[0].lower()
            # Flag obvious low-contrast combinations
            low_contrast_pairs = [
                ("white", "white"), ("#fff", "#fff"), ("#ffffff", "#ffffff"),
                ("gray", "gray"), ("grey", "grey"),
                ("#ccc", "#ddd"), ("#ddd", "#eee"), ("#eee", "#fff"),
            ]
            if (fg, bg) in low_contrast_pairs or fg == bg:
                violations.append(ViolationResult(
                    rule_id="color-contrast",
                    rule_name="Elements must have sufficient color contrast",
                    severity="serious",
                    wcag_criteria="1.4.3",
                    description=f"Inline styles set foreground '{fg}' and background '{bg}' which may not meet WCAG AA contrast ratio of 4.5:1.",
                    element_html=str(el)[:200],
                    selector=_build_selector(el),
                ))
    # Also flag light-on-light text patterns in common classes
    for el in soup.find_all(class_=True):
        class_str = " ".join(el.get("class", []))
        if re.search(r'text-gray-[23]00|text-white', class_str) and re.search(r'bg-white|bg-gray-[12]00', class_str):
            violations.append(ViolationResult(
                rule_id="color-contrast",
                rule_name="Elements must have sufficient color contrast",
                severity="serious",
                wcag_criteria="1.4.3",
                description="Element has utility classes suggesting light text on a light background, which may fail WCAG AA contrast requirements.",
                element_html=str(el)[:200],
                selector=_build_selector(el),
            ))

    # 12. Interactive elements missing accessible names (WCAG 4.1.2)
    for el in soup.find_all(["input", "select", "textarea"]):
        if el.get("type") in ("hidden", "submit", "button", "reset", "image"):
            continue
        # Already covered by form-label check, but also check ARIA specifically
        if el.get("role") and not el.get("aria-label") and not el.get("aria-labelledby"):
            title = el.get("title")
            if not title:
                violations.append(ViolationResult(
                    rule_id="aria-input-name",
                    rule_name="ARIA input fields must have accessible names",
                    severity="serious",
                    wcag_criteria="4.1.2",
                    description="Interactive element with a role attribute is missing an accessible name (aria-label, aria-labelledby, or title).",
                    element_html=str(el)[:200],
                    selector=_build_selector(el),
                ))

    # Check custom interactive elements (divs/spans with click handlers or roles)
    interactive_roles = {"button", "link", "tab", "menuitem", "checkbox", "radio", "switch", "slider", "textbox", "combobox"}
    for el in soup.find_all(attrs={"role": True}):
        role = el.get("role", "").lower()
        if role in interactive_roles:
            text = el.get_text(strip=True)
            aria = el.get("aria-label") or el.get("aria-labelledby") or el.get("title")
            if not text and not aria:
                violations.append(ViolationResult(
                    rule_id="aria-interactive-name",
                    rule_name="Interactive ARIA elements must have accessible names",
                    severity="critical",
                    wcag_criteria="4.1.2",
                    description=f"Element with role='{role}' has no accessible name. Screen reader users cannot identify this control.",
                    element_html=str(el)[:200],
                    selector=_build_selector(el),
                ))

    # 13. Auto-playing media without controls (WCAG 1.4.2)
    for media in soup.find_all(["audio", "video"]):
        if media.get("autoplay") is not None:
            if media.get("muted") is None:
                violations.append(ViolationResult(
                    rule_id="media-autoplay",
                    rule_name="Auto-playing media must be muted or have controls",
                    severity="serious",
                    wcag_criteria="1.4.2",
                    description="Media element auto-plays without being muted. This can be disorienting for screen reader users and disruptive for all users.",
                    element_html=str(media)[:200],
                    selector=_build_selector(media),
                ))

    page_result = PageResult(url=url, violations=violations)
    return page_result


def calculate_score(scan_result):
    """Calculate compliance score (0-100) based on violations."""
    if scan_result.total_violations == 0:
        return 100

    penalty = (
        scan_result.critical_count * 15
        + scan_result.serious_count * 8
        + scan_result.moderate_count * 3
        + scan_result.minor_count * 1
    )

    score = max(0, 100 - penalty)
    return score


def run_scan(base_url, max_pages=5):
    """Run a full accessibility scan on a website. Returns a ScanResult."""
    result = ScanResult()

    try:
        html = fetch_page(base_url)
    except Exception as e:
        page = PageResult(url=base_url, error=str(e))
        result.pages.append(page)
        result.score = 0
        return result

    # Scan the base page
    page_result = check_page(base_url, html)
    result.pages.append(page_result)

    # Discover and scan additional pages
    if max_pages > 1:
        extra_urls = discover_pages(base_url, html, max_pages)
        for url in extra_urls:
            try:
                page_html = fetch_page(url)
                pr = check_page(url, page_html)
                result.pages.append(pr)
            except Exception as e:
                result.pages.append(PageResult(url=url, error=str(e)))

    # Tally violations
    for page in result.pages:
        for v in page.violations:
            result.total_violations += 1
            if v.severity == "critical":
                result.critical_count += 1
            elif v.severity == "serious":
                result.serious_count += 1
            elif v.severity == "moderate":
                result.moderate_count += 1
            else:
                result.minor_count += 1

    result.score = calculate_score(result)
    return result


def _build_selector(tag):
    """Build a simple CSS selector for an element."""
    parts = [tag.name]
    if tag.get("id"):
        parts.append(f"#{tag['id']}")
    elif tag.get("class"):
        classes = ".".join(tag["class"][:2])
        parts.append(f".{classes}")
    return "".join(parts)
