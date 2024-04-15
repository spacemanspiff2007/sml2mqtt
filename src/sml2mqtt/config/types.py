from typing import Annotated, Literal, TypeAlias

from pydantic import Strict, StrictFloat, StrictInt, StringConstraints

from sml2mqtt.__log__ import get_logger


log = get_logger('config')


ObisHex = Annotated[
    str,
    StringConstraints(to_lower=True, strip_whitespace=True, pattern=r'[0-9a-fA-F]{12}', strict=True)
]

LowerStr = Annotated[
    str,
    StringConstraints(to_lower=True, strip_whitespace=True, strict=True)
]


Number: TypeAlias = StrictInt | StrictFloat

PercentStr = Annotated[str, Strict(), StringConstraints(strip_whitespace=True, pattern=r'^\d+\.?\d*\s*%$')]

StrippedStr = Annotated[str, Strict(), StringConstraints(strip_whitespace=True)]

MqttTopicStr = Annotated[str, Strict(), StringConstraints(strip_whitespace=True, min_length=1)]
MqttQosInt: TypeAlias = Literal[0, 1, 2]
