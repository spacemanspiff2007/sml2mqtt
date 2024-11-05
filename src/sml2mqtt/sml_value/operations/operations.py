from collections.abc import Generator

from typing_extensions import override

from sml2mqtt.sml_value.base import OperationContainerBase, SmlValueInfo, ValueOperationBase


class OrOperation(ValueOperationBase, OperationContainerBase):

    @override
    def process_value(self, value: float | None, info: SmlValueInfo) -> float | None:
        ret: float | None = None
        for op in self.operations:
            if (call := op.process_value(value, info)) is not None and ret is None:
                ret = call

        return ret

    def __repr__(self) -> str:
        return f'<Or at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Or:'
        for o in self.operations:
            yield from o.describe(indent + '  ')


class SequenceOperation(ValueOperationBase, OperationContainerBase):
    @override
    def process_value(self, value: float | None, info: SmlValueInfo) -> float | None:
        for op in self.operations:
            value = op.process_value(value, info)
        return value

    def __repr__(self) -> str:
        return f'<Sequence at 0x{id(self):x}>'

    @override
    def describe(self, indent: str = '') -> Generator[str, None, None]:
        yield f'{indent:s}- Sequence:'
        for o in self.operations:
            yield from o.describe(indent + '  ')
