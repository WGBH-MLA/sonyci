from loguru import logger as log
from rich.logging import RichHandler

log.configure(
    handlers=[
        {
            'sink': RichHandler(),
        }
    ]
)
