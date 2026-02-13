"""
Shared constants and configuration for the PageGuard agent system.
Single source of truth - no duplication across modules.
"""

import os

# --- Model Configuration ---
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

# --- ADA Deadline (configurable for future regulations) ---
ADA_DEADLINE_YEAR = int(os.environ.get("ADA_DEADLINE_YEAR", "2026"))
ADA_DEADLINE_MONTH = int(os.environ.get("ADA_DEADLINE_MONTH", "4"))
ADA_DEADLINE_DAY = int(os.environ.get("ADA_DEADLINE_DAY", "24"))

# --- Severity Weights (used for priority scoring) ---
SEVERITY_WEIGHTS = {
    "critical": 4,
    "serious": 3,
    "moderate": 2,
    "minor": 1,
}

# --- Effort Estimates Per Rule (minutes) ---
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

# Default effort for unknown rules
DEFAULT_EFFORT = {"min": 5, "max": 15, "label": "Moderate"}

# --- Agent Limits ---
MAX_AGENT_ITERATIONS = 10
AGENT_API_TIMEOUT = 30  # seconds
OPENAI_API_TIMEOUT = 20  # seconds
MAX_CONTEXT_LENGTH = 4000  # characters for inter-agent context
MAX_QUESTION_LENGTH = 500  # characters for user questions

# --- Score Thresholds ---
SCORE_COMPLIANT = 90
SCORE_NEEDS_WORK = 70
SCORE_AT_RISK = 50


def get_ada_deadline():
    """Return the ADA deadline as a datetime object."""
    from datetime import datetime
    return datetime(ADA_DEADLINE_YEAR, ADA_DEADLINE_MONTH, ADA_DEADLINE_DAY)


def days_until_deadline():
    """Return days remaining until ADA deadline."""
    from datetime import datetime
    remaining = (get_ada_deadline() - datetime.now()).days
    return max(0, remaining)


def format_effort(minutes: int) -> str:
    """Format effort minutes into human-readable string."""
    if minutes >= 60:
        return f"{minutes // 60}h {minutes % 60}m"
    return f"{minutes} min"


def get_effort_for_rule(rule_id: str) -> dict:
    """Get effort estimate for a rule, with fallback."""
    return EFFORT_ESTIMATES.get(rule_id, DEFAULT_EFFORT)
