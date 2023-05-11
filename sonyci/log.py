from loguru import logger as log

try:
    from rich.logging import RichHandler

    log.configure(
        handlers=[
            {
                'sink': RichHandler(),
            }
        ]
    )

except ImportError:
    pass
