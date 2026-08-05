import sys
from os import environ as env

from loguru import logger as log

LOG_LEVEL = env.get('LOG_LEVEL', 'INFO')

try:
    from rich.console import Console
    from rich.logging import RichHandler

    # RichHandler renders its own time/level, so only pass the message.
    _sink = RichHandler(console=Console(stderr=True), rich_tracebacks=True, log_time_format='[%H:%M:%S.%f]')
    _format = '{message}'
except ImportError:
    _sink = sys.stderr
    _format = '{time:YYYY-MM-DD HH:mm:ss.SSS} {level} {message}'


def configure(level: str = LOG_LEVEL) -> None:
    """(Re)configure logging to emit ``sonyci`` records at ``level``."""
    log.remove()
    log.add(_sink, format=_format, filter='sonyci', level=level)


configure()
