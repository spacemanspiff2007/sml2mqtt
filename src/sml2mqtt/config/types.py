from typing import Annotated, TypeAlias

from annotated_types import Interval
from pydantic import StrictFloat, StrictInt, StringConstraints


ObisHex = Annotated[
    str,
    StringConstraints(to_lower=True, strip_whitespace=True, pattern=r'[0-9a-fA-F]{12}')
]

LowerStr = Annotated[
    str,
    StringConstraints(to_lower=True, strip_whitespace=True, strict=True)
]


Number: TypeAlias = StrictInt | StrictFloat

PercentStr = Annotated[str, StringConstraints(strip_whitespace=True, pattern=r'^\d+\.?\d*\s*%$')]

StrippedStr = Annotated[str, StringConstraints(strip_whitespace=True)]

MqttTopicStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
MqttQosInt = Annotated[int, Interval(ge=0, le=2)]
