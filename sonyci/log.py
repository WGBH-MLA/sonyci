from loguru import logger as log
from rich.logging import RichHandler

log.configure(
    handlers=[
        {
            'sink': RichHandler(),
            'format': '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>',  # noqa: E501
        }
    ]
)
