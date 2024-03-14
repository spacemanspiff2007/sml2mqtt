from sml2mqtt.sml_device import SmlDevice


def test_device_setup(no_mqtt, caplog, sml_data_1: bytes, arg_analyze):
    device = SmlDevice('testing')
