import logging
from logging.handlers import RotatingFileHandler


def configure_logging():
    # Create a logger
    logger = logging.getLogger("flask_app")
    logger.setLevel(logging.DEBUG)  # Adjust log level as needed

    # Define log formatter
    formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s]: %(message)s")

    # Create a rotating file handler (5MB max size, 5 backup files)
    file_handler = RotatingFileHandler(
        "flask.log", maxBytes=5 * 1024 * 1024, backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(file_handler)

    # Optionally log to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Use INFO for less verbose logs
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Prevent Flask's default logger from duplicating logs
    flask_logger = logging.getLogger("werkzeug")
    flask_logger.setLevel(
        logging.ERROR
    )  # Silence Werkzeug logs or set appropriate level
    flask_logger.handlers = [file_handler, console_handler]

    return logger
