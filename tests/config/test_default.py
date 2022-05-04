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
- url: COM1
  timeout: 3
- url: /dev/ttyS0
  timeout: 3
devices:   # Device configuration by ID or url
  DEVICE_ID_HEX:
    mqtt:
      topic: DEVICE_BASE_TOPIC
    status:
      topic: status
    skip:
    - OBIS
    values:
      OBIS:
        mqtt:
          topic: OBIS
        workarounds:
        - negative on energy meter status: true
        transformations:
        - factor: 3
        - offset: 100
        - round: 2
        filters:
        - diff: 10
        - perc: 10
        - every: 120
'''
