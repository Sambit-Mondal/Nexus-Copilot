"""
Nexus FastAPI Gateway Package
"""

__version__ = "1.0.0"
__author__ = "Nexus Team"

from app.config import settings
from app.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

logger.info(f"Nexus Gateway v{__version__} initialized")
