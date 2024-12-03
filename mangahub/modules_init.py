from directories import *

import rich.traceback
from rich import print as rich_print
rich.traceback.install(show_locals=True)

from loguru import logger
logger.add(f"{LOG_DIR}/log-{{time}}.log", format="{time} {level} {message}", level="DEBUG", retention=10)