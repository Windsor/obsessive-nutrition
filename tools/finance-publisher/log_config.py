"""Shared logging configuration for finance-publisher."""
import os
import logging
from datetime import datetime

LOG_DIR = os.path.expanduser("~/finance-publisher/logs")
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name):
    log_file = os.path.join(LOG_DIR, f"publish-{datetime.now().strftime('%Y-%m-%d')}.log")
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler(log_file)
        fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        sh = logging.StreamHandler()
        sh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        logger.addHandler(fh)
        logger.addHandler(sh)
    return logger
