import logging
import sys

def set_debug():
    logger.setLevel(logging.DEBUG)
    logging.debug("Debug enabled")

if sys.stderr.isatty():
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD_RED = '\033[1;91m'
    RESET = '\033[0m'
else:
    BLUE = ''
    GREEN = ''
    YELLOW = ''
    RED = ''
    BOLD_RED = ''
    RESET = ''

class ColoredFormatter(logging.Formatter):
    # Define color codes
    COLORS = {
        'DEBUG': BLUE,
        'INFO': GREEN,
        'WARNING': YELLOW,
        'ERROR': RED,
        'CRITICAL': BOLD_RED,
    }
    RST = RESET

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RST)
        record.relativeSeconds = record.relativeCreated / 1000
        message = super().format(record)

        if sys.stderr.isatty():
            return f"{log_color}{message}{self.RST}"
        else:
            return message


def build_handlers(log_format: str) -> list:
    formatter = ColoredFormatter(log_format)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    return [handler]

logging.basicConfig(level=logging.INFO, handlers=build_handlers('T:%(relativeSeconds).2f [%(levelname)s] %(message)s'))
logger = logging.getLogger("HighHeat")
logging.debug("Logger initialized")
