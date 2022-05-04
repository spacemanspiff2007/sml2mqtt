import logging
from pathlib import Path

from easyconfig import BaseModel
from pydantic import Extra, Field, validator


class LoggingSettings(BaseModel):
    level: str = Field('INFO', description='Log level')
    file: Path = Field('sml2mqtt.log', description='Log file path (absolute or relative to config file)')

    class Config:
        extra = Extra.forbid

    @validator('level')
    def validate_logging(cls, value):
        if value not in logging._nameToLevel:
            raise ValueError(f'Level must be one of {", ".join(logging._nameToLevel)}')
        return value

    def set_log_level(self) -> int:
        level = logging._nameToLevel[self.level]
        logging.getLogger().setLevel(level)
        return level
