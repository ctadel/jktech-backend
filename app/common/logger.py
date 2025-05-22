import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys
from app.config import settings

LOG_DIR = Path(settings.LOG_DIRECTORY)
LOG_DIR.mkdir(exist_ok=True)

# -- ACCESS LOGGING SETUP --
access_log_handler = RotatingFileHandler(LOG_DIR / "access.log")
access_log_formatter = logging.Formatter(
    '%(asctime)s - %(message)s'
)
access_log_handler.setFormatter(access_log_formatter)
access_logger = logging.getLogger("access-log")
access_logger.setLevel(logging.INFO)
access_logger.addHandler(access_log_handler)


# -- APPLICATION LOGGING SETUP --
app_log_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(app_log_formatter)

app_log_path = LOG_DIR / "app.log"
file_handler = RotatingFileHandler(app_log_path)
file_handler.setFormatter(app_log_formatter)

logger = logging.getLogger(settings.PROJECT_NAME)
logger.setLevel(logging.DEBUG)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

logging.getLogger("sqlalchemy.engine").setLevel(logging.CRITICAL)
