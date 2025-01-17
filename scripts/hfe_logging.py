import logging
from logging.handlers import RotatingFileHandler
import os


def configure_logging():
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # Create logger
    logger = logging.getLogger("flask_app")
    logger.setLevel(logging.ERROR)

    # Define log formatter
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(process)d]: %(message)s"
    )

    # Concurrent rotating file handler
    file_handler = RotatingFileHandler(
        "logs/flask.log", maxBytes=5 * 1024 * 1024, backupCount=5
    )
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(file_handler)

    # Optionally, log to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
