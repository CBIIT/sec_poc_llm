import os
import sys

from loguru import logger

logger.remove()
logger.add(sys.stdout, level=os.getenv("LOGLEVEL", "INFO"))
