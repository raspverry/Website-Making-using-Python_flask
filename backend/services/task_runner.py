"""Simple background task runner using threads.
For MVP, this is sufficient. Migrate to Celery/ARQ when scaling beyond ~100 concurrent users.
"""
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Callable

logger = logging.getLogger(__name__)

# Thread pool for background tasks (limit concurrent scans)
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="scan-worker")

# Maximum time a single scan can run (5 minutes)
SCAN_TIMEOUT_SECONDS = 300


def run_in_background(func: Callable, *args, **kwargs):
    """Submit a function to run in the background thread pool."""
    future = _executor.submit(func, *args, **kwargs)
    future.add_done_callback(_log_errors)
    return future


def _log_errors(future):
    """Log any exceptions from background tasks."""
    try:
        future.result(timeout=0)
    except TimeoutError:
        pass
    except Exception as e:
        logger.error("Background task failed: %s", e, exc_info=True)
