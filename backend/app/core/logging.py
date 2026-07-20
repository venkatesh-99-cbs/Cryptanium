"""
Centralized Logging Configuration for Cryptanium Backend.
"""

import logging
import sys


def setup_logging(log_level: str = "INFO"):
    """Configures root logger for standard output with level and timestamp formatting."""
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove default handlers if any
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)
        
    root_logger.addHandler(handler)
    logging.getLogger("uvicorn.access").handlers = [handler]
