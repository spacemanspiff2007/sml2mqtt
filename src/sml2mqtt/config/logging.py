import logging

from easyconfig import BaseModel
from pydantic import Field, field_validator


class LoggingSettings(BaseModel):
    level: str = Field('INFO', description='Log level')
    file: str = Field('sml2mqtt.log', description='Log file path (absolute or relative to config file) or "stdout"')

    @field_validator('level')
    def validate_logging(cls, value):
        if value not in logging._nameToLevel:
            msg = f'Level must be one of {", ".join(logging._nameToLevel)}'
            raise ValueError(msg)
        return value

    def set_log_level(self) -> int:
        level = logging._nameToLevel[self.level]
        logging.getLogger().setLevel(level)
        return level
