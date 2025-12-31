"""Centralized logging configuration"""

import logging
import logging.handlers
import sys
import json
from pathlib import Path
from datetime import datetime

# Create logs directory
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_obj = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "path": record.pathname
        }
        
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_obj)


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[41m',   # Red background
    }
    RESET = '\033[0m'
    
    def format(self, record):
        if sys.platform == "win32":
            # Windows doesn't support ANSI colors well, so skip coloring
            return super().format(record)
        
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
        return super().format(record)


def setup_logger(name: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    Setup and return a configured logger instance
    
    Args:
        name: Logger name (module name)
        level: Logging level (default: INFO)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name or __name__)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Console handler with color
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = ColoredFormatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler - rotating file
    log_file = LOG_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_formatter = JSONFormatter()
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger


# Create module-level logger
logger = setup_logger(__name__)