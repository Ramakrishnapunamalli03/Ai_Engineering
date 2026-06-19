"""Exponential-backoff retry for provider calls."""
import time

RETRYABLE_STATUS = {429, 500, 502, 503, 504}

def with_retry(call, *, max_retries: int = 3, base_delay: float = 0.5):
    """Run call(); on a transient (429/5xx) error, back off and retry. Re-raise the rest."""
    for attempt in range(max_retries + 1):
        try:
            return call()
        except Exception as err:
            status = getattr(err, "status_code", None) or getattr(err, "code", None)
            if status not in RETRYABLE_STATUS or attempt == max_retries:
                raise
            time.sleep(base_delay * (2 ** attempt))  # 0.5s, 1s, 2s, ...


def retry_call(call, *args, **kwargs):
    return with_retry(lambda: call(*args, **kwargs))