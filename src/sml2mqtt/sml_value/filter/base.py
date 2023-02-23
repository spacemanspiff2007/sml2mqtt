from sml2mqtt.sml_value.__types__ import VALUE_TYPE


class FilterBase:
    def required(self, value: VALUE_TYPE) -> VALUE_TYPE:
        raise NotImplementedError()

    def done(self, value):
        raise NotImplementedError()
