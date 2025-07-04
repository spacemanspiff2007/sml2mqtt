import re

from sml2mqtt.config import CONFIG


def test_default() -> None:
    yaml = CONFIG.generate_default_yaml()

    # Replace dynamically created identifier
    yaml = re.sub(r'identifier: sml2mqtt-\w+', 'identifier: sml2mqtt-A1b2', yaml)

    assert '\n' + yaml == '''
logging:
  level: INFO         # Log level
  file: sml2mqtt.log  # Log file path (absolute or relative to config file) or "stdout"
mqtt:
  connection:
    identifier: sml2mqtt-A1b2
    host: localhost
    port: 1883
    user: ''
    password: ''
  topic prefix: sml2mqtt   # Prefix for all topics. Set to empty string to disable
  defaults:
    qos: 0         # Default value for QoS if no other QoS value in the config entry is set
    retain: false  # Default value for retain if no other retain value in the config entry is set
  last will:
    topic: status   # Topic fragment for building this topic with the parent topic
general:
  Wh in kWh: true       # Automatically convert Wh to kWh
  republish after: 120  # Republish automatically after this time (if no other filter configured)
inputs:
- type: serial
  url: COM1   # Device path
  timeout: 6  # Seconds after which a timeout will be detected (default=6)
- type: serial
  url: /dev/ttyS0   # Device path
  timeout: 6        # Seconds after which a timeout will be detected (default=6)
devices:   # Device configuration by ID or url
  device_id_hex:
    mqtt:    # Optional MQTT configuration for this meter.
      topic: DEVICE_BASE_TOPIC   # Topic fragment for building this topic with the parent topic
    status:  # Optional MQTT status topic configuration for this meter
      topic: status   # Topic fragment for building this topic with the parent topic
    skip:    # OBIS codes (HEX) of values that will not be published (optional)
    - '00112233445566'
    values:  # Configurations for each of the values (optional)
    - obis: '00112233445566'   # Obis code for this value
      mqtt:                    # Mqtt config for this value (optional)
        topic: OBIS   # Topic fragment for building this topic with the parent topic
      operations:              # A sequence of operations that will be evaluated one after another.
                               # If one operation blocks this will return nothing.
      - negative on energy meter status: true   # Set to "true" to enable or to "false" to disable workaround. If the default obis code for the energy meter is wrong set to the appropriate meter obis code instead
      - factor: 3   # Factor with which the value gets multiplied
      - offset: 100   # Offset that gets added on the value
      - round: 2   # Round to the specified digits, negative for tens
      - type: change filter   # Filter which passes only changes
      - refresh action: 600   # Refresh interval
'''
