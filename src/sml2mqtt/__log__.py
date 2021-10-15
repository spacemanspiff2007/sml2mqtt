import logging
import sys
from datetime import date, datetime
from logging.handlers import RotatingFileHandler

import sml2mqtt

log = logging.getLogger('sml')


def get_logger(suffix: str) -> logging.Logger:
    if not suffix:
        return log
    return log.getChild(suffix)


class MidnightRotatingFileHandler(RotatingFileHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_check: date = datetime.now().date()

    def shouldRollover(self, record):
        date = datetime.now().date()
        if date == self.last_check:
            return 0
        self.last_check = date
        return super().shouldRollover(record)


def setup_log():
    level = sml2mqtt.CONFIG.logging.set_log_level()

    # This is the longest logger name str
    chars = 0
    for device in sml2mqtt.CONFIG.ports:
        chars = max(len(f'sml.device.{device.url}'), chars)
    log_format = logging.Formatter("[{asctime:s}] [{name:" + str(chars) + "s}] {levelname:8s} | {message:s}", style='{')

    # File Handler
    log_file = sml2mqtt.CONFIG.logging.file
    if not log_file.is_absolute():
        log_file = sml2mqtt.CMD_ARGS.config.parent / log_file
        log_file.resolve()

    handler = MidnightRotatingFileHandler(
        str(log_file), maxBytes=1024 * 1024, backupCount=3, encoding='utf-8'
    )
    handler.setFormatter(log_format)
    handler.setLevel(logging.DEBUG)

    # Bind handler to logger
    root_log = logging.getLogger()
    root_log.addHandler(handler)

    # If we analyze we print, too
    if sml2mqtt.CMD_ARGS.analyze:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(level)
        ch.setFormatter(log_format)
        root_log.addHandler(ch)

    log.info(f'Starting V{sml2mqtt.__version__}')
