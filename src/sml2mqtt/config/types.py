from typing import Annotated, TypeAlias

from pydantic import StrictFloat, StrictInt, StringConstraints


ObisHex = Annotated[
    str,
    StringConstraints(to_lower=True, strip_whitespace=True, pattern=r'[0-9a-fA-F]{12}')
]

Number: TypeAlias = StrictInt | StrictFloat

TimeInSeconds = Annotated[
    Number,
    'asdf'
]
