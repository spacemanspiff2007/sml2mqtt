from collections.abc import Generator

from typing_extensions import override

from sml2mqtt.sml_value.base import OperationContainerBase, SmlValueInfo, ValueOperationBase


class OrOperation(ValueOperationBase, OperationContainerBase):

    @override
    def process_value(self, value: float, info: SmlValueInfo) -> float | None:
        for op in self.operations:
            if (ret := op.process_value(value, info)) is not None:
                return ret

        return None

    def __repr__(self):
        return f'<Or at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Or:'
        for o in self.operations:
            yield from o.describe(indent + '  ')


class SequenceOperation(ValueOperationBase, OperationContainerBase):
    @override
    def process_value(self, value: float, info: SmlValueInfo) -> float | None:
        for op in self.operations:
            if (value := op.process_value(value, info)) is None:
                return None
        return value

    def __repr__(self):
        return f'<Sequence at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Sequence:'
        for o in self.operations:
            yield from o.describe(indent + '  ')
