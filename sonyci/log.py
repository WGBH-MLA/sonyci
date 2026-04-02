from loguru import logger as log

try:
    from rich.logging import RichHandler, Console

    log.configure(
        handlers=[
            {
                'sink': RichHandler(console=Console(stderr=True)),
            }
        ]
    )

except ImportError:
    pass
