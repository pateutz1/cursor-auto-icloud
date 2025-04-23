import logging
import os
from datetime import datetime
import sys

# Global variable to track if logger has been initialized
_logger_initialized = False

def initialize_logger():
    """Initialize logger if not already initialized"""
    global _logger_initialized
    
    if _logger_initialized:
        return
    
    # Configure logging
    # If running as frozen executable, use the executable's directory
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        # Otherwise use the project root directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    log_dir = os.path.join(base_dir, "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    class PrefixFormatter(logging.Formatter):
        """Custom formatter to add open source project prefix for DEBUG level logs"""

        def format(self, record):
            if record.levelno == logging.DEBUG:  # Only add prefix for DEBUG level
                record.msg = f"[Open Source Project: https://github.com/pateutz1/cursor-auto-icloud] {record.msg}"
            return super().format(record)

    # Clear any existing handlers
    root_logger = logging.getLogger()
    if root_logger.handlers:
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

    # Configure basic logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(
                os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log"),
                encoding="utf-8",
            ),
        ],
    )

    # Set custom formatter for file handlers
    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.FileHandler):
            handler.setFormatter(
                PrefixFormatter("%(asctime)s - %(levelname)s - %(message)s")
            )

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(PrefixFormatter("%(message)s"))

    # Add console handler to logger
    logging.getLogger().addHandler(console_handler)

    # Print log directory path
    logging.info(f"Logger initialized, log directory: {os.path.abspath(log_dir)}")
    
    _logger_initialized = True

# Initialize logger when module is imported
initialize_logger()

# Rest of the original code
def main_task():
    """
    Main task execution function. Simulates a workflow and handles errors.
    """
    try:
        logging.info("Starting the main task...")

        # Simulated task and error condition
        if some_condition():
            raise ValueError("Simulated error occurred.")

        logging.info("Main task completed successfully.")

    except ValueError as ve:
        logging.error(f"ValueError occurred: {ve}", exc_info=True)
    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}", exc_info=True)
    finally:
        logging.info("Task execution finished.")


def some_condition():
    """
    Simulates an error condition. Returns True to trigger an error.
    Replace this logic with actual task conditions.
    """
    return True


if __name__ == "__main__":
    # Application workflow
    logging.info("Application started.")
    main_task()
    logging.info("Application exited.")
