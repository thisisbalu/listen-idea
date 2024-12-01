import socket
import time
import logging

def is_internet_available():
    """Check if the internet is available by pinging a reliable host."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False


def retry_on_internet_issue(func, retry_interval=30, *args, **kwargs):
    """
    Retry a function if there's an internet issue.
    Returns the function's result once successful.
    """
    while True:
        if is_internet_available():
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.warning(f"Function {func.__name__} failed: {e}. Retrying...")
        else:
            logging.warning("Internet is not available. Retrying...")
        time.sleep(retry_interval)
