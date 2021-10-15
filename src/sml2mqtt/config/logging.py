import logging
from pathlib import Path

from easyconfig import ConfigModel
from pydantic import Field, validator


class LoggingSettings(ConfigModel):
    level: str = Field('INFO', description='Log level')
    file: Path = Field('sml2mqtt.log', description='Log file path (absolute or relative to config file)')

    @validator('level')
    def validate_logging(cls, value):
        if value not in logging._nameToLevel:
            raise ValueError(f'Level must be one of {", ".join(logging._nameToLevel)}')
        return value

    def set_log_level(self) -> int:
        level = logging._nameToLevel[self.level]
        logging.getLogger().setLevel(level)
        return level
