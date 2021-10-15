from typing import Dict, TypeVar

from smllib.sml import SmlListEntry

from sml2mqtt.value.__types__ import WORKAROUND_TYPE


class WorkaroundBase:
    def __init__(self, arg: WORKAROUND_TYPE):
        self.enabled = True
        if arg is False:
            self.enabled = False

    def fix(self, value: SmlListEntry, frame_values: Dict[str, SmlListEntry]) -> SmlListEntry:
        raise NotImplementedError()

    def __repr__(self):
        return f'<{self.__class__.__name__}>'


WORKAROUND_OBJ = TypeVar('WORKAROUND_OBJ', bound=WorkaroundBase)
