import os
import orjson
import logging
from datetime import datetime
from typing import Any

class StructuredMessage:
    """Emits a message and then any additional keyword arguments as JSON."""

    def __init__(self, message: str, **kwargs: Any):
        self.message = message
        self.kwargs = kwargs

    def __str__(self) -> str:
        if self.kwargs:
            return f'{self.message} >>> {orjson.dumps(self.kwargs).decode("utf-8")}'
        return self.message

_ = StructuredMessage

log_format = "[%(asctime)s] %(lineno)d - %(filename)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s"
now = datetime.now()

LOG_FILE_FOLDER = now.strftime('%m_%d_%Y')
LOG_FILE = now.strftime('%H-%M-%S') + ".log"

logs_path = os.path.join(os.getcwd(), 'logs', LOG_FILE_FOLDER)
os.makedirs(logs_path, exist_ok=True)

LOG_FILE_PATH = os.path.join(logs_path, LOG_FILE)

# Default to INFO level, can be overridden when calling setup_logger
DEFAULT_LOG_LEVEL = logging.INFO

def setup_logger(project_name: str, debug: bool = False) -> logging.Logger:
    log_level = logging.DEBUG if debug else logging.INFO
    
    logging.basicConfig(filename=LOG_FILE_PATH, level=log_level, format=log_format)
    logger = logging.getLogger(project_name)

    # Add a stream handler to output logs to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(console_handler)

    return logger

# Create a default logger
logger = setup_logger("DefaultProject")