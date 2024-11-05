import logging
import sys
from datetime import date, datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

import sml2mqtt


log = logging.getLogger('sml')


def get_logger(suffix: str) -> logging.Logger:
    if not suffix:
        return log
    return log.getChild(suffix)


class MidnightRotatingFileHandler(RotatingFileHandler):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.last_check: date = datetime.now().date()

    def shouldRollover(self, record) -> int:
        if (date_now := datetime.now().date()) == self.last_check:
            return 0
        self.last_check = date_now
        return super().shouldRollover(record)


def setup_log() -> None:
    level = sml2mqtt.CONFIG.logging.set_log_level()

    # This is the longest logger name str
    chars = 0
    for device in sml2mqtt.CONFIG.inputs:
        # Name of the longest logger, should be the device status
        chars = max(len(get_logger(device.get_device_name()).getChild('status').name), chars)
    log_format = logging.Formatter('[{asctime:s}] [{name:' + str(chars) + 's}] {levelname:8s} | {message:s}', style='{')

    # File Handler
    file_path = sml2mqtt.CONFIG.logging.file
    if file_path.lower() == 'stdout':
        handler = logging.StreamHandler(sys.stdout)
    else:
        log_file = Path(file_path)
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
