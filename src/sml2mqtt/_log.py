import logging
import sys
from datetime import date, datetime
from logging.handlers import RotatingFileHandler

import sml2mqtt
import sml2mqtt._args


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
    lvl = sml2mqtt.CONFIG.log.level

    # This is the longest logger name str
    chars = 0
    for device in sml2mqtt.CONFIG.devices:
        chars = max(len(f'sml.device.{device.device}'), chars)
    log_format = logging.Formatter("[{asctime:s}] [{name:" + str(chars) + "s}] {levelname:8s} | {message:s}", style='{')

    handler = MidnightRotatingFileHandler(
        str(sml2mqtt.CONFIG.log.file), maxBytes=1024 * 1024, backupCount=3, encoding='utf-8'
    )
    handler.setFormatter(log_format)
    handler.setLevel(logging.DEBUG)

    # Bind handler to logger
    root = logging.getLogger()
    root.setLevel(lvl)
    root.addHandler(handler)

    if sml2mqtt._args.ARGS.analyze:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(lvl)
        ch.setFormatter(log_format)
        root.addHandler(ch)
