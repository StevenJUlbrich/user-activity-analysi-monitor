from functools import wraps
from loguru import logger
import traceback

def handle_errors(error_callback=None, log_errors=True):
    """
    Decorator for consistent error handling.
    
    Args:
        error_callback: Function to call on error (e.g., show UI message)
        log_errors: Whether to log errors
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(f"Error in {func.__name__}: {str(e)}")
                    logger.debug(traceback.format_exc())
                    
                if error_callback:
                    error_callback(str(e))
                    
                # Re-raise if it's a critical error
                if isinstance(e, (SystemExit, KeyboardInterrupt)):
                    raise
                    
                return None
        return wrapper
    return decorator

# User-friendly error messages mapping
ERROR_MESSAGES = {
    "ORA-01017": "Invalid username/password. Please check your credentials.",
    "ORA-12154": "Cannot find database. Please check your database configuration.",
    "ORA-12170": "Connection timeout. Please check network connectivity.",
    "Kerberos": "Kerberos authentication failed. Please run 'kinit' and try again.",
    "Permission denied": "Access denied. Please check file permissions.",
    "No such file": "Configuration file not found. Please check the path.",
}

def get_user_friendly_error(technical_error: str) -> str:
    """Convert technical error to user-friendly message."""
    for key, message in ERROR_MESSAGES.items():
        if key in technical_error:
            return message
    return "An unexpected error occurred. Please check the logs for details."