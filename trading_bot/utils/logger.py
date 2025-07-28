import sys
import os
from loguru import logger
from ..config.settings import settings


def setup_logger():
    """
    Setup konfigurasi logger untuk aplikasi
    """
    # Remove default logger
    logger.remove()
    
    # Pastikan direktori logs ada
    log_dir = os.path.dirname(settings.log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Console logging
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True
    )
    
    # File logging
    logger.add(
        settings.log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )
    
    # Error file logging
    error_log_file = settings.log_file.replace('.log', '_error.log')
    logger.add(
        error_log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="5 MB",
        retention="30 days",
        compression="zip"
    )
    
    logger.info("Logger setup completed")


def get_logger(name: str = None):
    """
    Mendapatkan logger instance
    """
    if name:
        return logger.bind(name=name)
    return logger