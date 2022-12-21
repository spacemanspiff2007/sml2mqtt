from sml2mqtt.config import CONFIG


def test_default():

    yaml = CONFIG.generate_default_yaml()
    assert '\n' + yaml == '''
logging:
  level: INFO         # Log level
  file: sml2mqtt.log  # Log file path (absolute or relative to config file)
mqtt:
  connection:
    client id: sml2mqtt
    host: localhost
    port: 1883
    user: ''
    password: ''
    tls: false
    tls insecure: false
  topic prefix: sml2mqtt
  defaults:
    qos: 0         # Default value for QOS if no other QOS value in the config entry is set
    retain: false  # Default value for retain if no other retain value in the config entry is set
  last will:
    topic: status
general:
  Wh in kWh: true       # Automatically convert Wh to kWh
  republish after: 120  # Republish automatically after this time (if no other filter configured)
ports:
- url: COM1   # Device path
  timeout: 3  # Seconds after which a timeout will be detected (default=3)
- url: /dev/ttyS0   # Device path
  timeout: 3        # Seconds after which a timeout will be detected (default=3)
devices:   # Device configuration by ID or url
  DEVICE_ID_HEX:
    mqtt:
      topic: DEVICE_BASE_TOPIC
    status:
      topic: status
    skip:    # OBIS codes (HEX) of values that will not be published (optional)
    - OBIS
    values:  # Special configurations for each of the values (optional)
      OBIS:
        mqtt:             # Mqtt config for this entry (optional)
          topic: OBIS
        workarounds:      # Workarounds for the value (optional)
        - negative on energy meter status: true
        transformations:  # Mathematical transformations for the value (optional)
        - factor: 3
        - offset: 100
        - round: 2
        filters:          # Refresh options for the value (optional)
        - diff: 10
        - perc: 10
        - every: 120
'''
