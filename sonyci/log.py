from loguru import logger as log

try:
    from rich.logging import Console, RichHandler

    log.configure(
        handlers=[
            {
                'sink': RichHandler(console=Console(stderr=True)),
            }
        ]
    )

except ImportError:
    pass
