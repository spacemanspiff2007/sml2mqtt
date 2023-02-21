from sml2mqtt.sml_value.__types__ import VALUE_TYPE


class TransformationBase:
    def process(self, value: VALUE_TYPE) -> VALUE_TYPE:
        raise NotImplementedError()
