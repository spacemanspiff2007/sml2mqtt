from typing_extensions import override

from sml2mqtt.sml_value.base import SmlValueInfo, ValueOperationBase


class OrOperation(ValueOperationBase):
    def __init__(self):
        self.operations: tuple[ValueOperationBase, ...] = ()

    def add_operation(self, operation: ValueOperationBase):
        self.operations = (*self.operations, operation)

    @override
    def process_value(self, value: float, info: SmlValueInfo) -> float | None:
        for op in self.operations:
            if (ret := op.process_value(value, info)) is not None:
                return ret

        return None

    def __repr__(self):
        return f'<Or at 0x{id(self):x}>'
