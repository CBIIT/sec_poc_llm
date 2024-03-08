import sys

from loguru import logger


def configure(level="INFO", sink=sys.stdout):
    logger.remove()
    logger.add(
        sink,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=level,
    )


CONFIGURED = False

if not CONFIGURED:
    configure()
    CONFIGURED = True
