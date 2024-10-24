import time
from functools import wraps
from gui.utils import MessageManager

def retry(max_retries=5, delay=1, exception_to_check=Exception):
    """
    Retry decorator that retries a function call if it raises an exception.
    max_retries: Number of retry attempts.
    delay: Delay between retries (in seconds).
    exception_to_check: The exception type to catch for retrying.
    """
    def decorator_retry(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except exception_to_check as e:
                    retries += 1
                    MessageManager.get_instance().show_message(
                        'info', f"Attempt {retries}/{max_retries} failed: {str(e)}", duration=2000
                    )

            MessageManager.get_instance().show_message(
                'error', f"Function {func.__name__} failed after {max_retries} attempts.", duration=5000
            )
            return None
        return wrapper
    return decorator_retry
