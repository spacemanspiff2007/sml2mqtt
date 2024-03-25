**************************************
Configuration & CLI
**************************************

.. _COMMAND_LINE_INTERFACE:

Command Line Interface
======================================

.. exec_code::
    :hide_code:

    import sml2mqtt.__args__
    sml2mqtt.__args__.get_command_line_args(['-h'])


Configuration
======================================

Configuration is done through ``config.yml`` The parent folder of the file can be specified with ``-c PATH`` or ``--config PATH``.
If nothing is specified the file ``config.yml`` is searched in the subdirectory ``sml2mqtt`` in

* the current working directory
* the venv directory
* the user home

If the config is specified and it does not yet exist a default configuration file will be created

Example
--------------------------------------

.. py:currentmodule:: sml2mqtt.config.config


..
    YamlModel: Settings

.. code-block:: yaml

    logging:
      level: INFO         # Log level
      file: sml2mqtt.log  # Log file path (absolute or relative to config file) or stdout

    mqtt:
      connection:
        identifier: sml2mqtt-ZqlFvhSBdDGvJ
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
        topic: status   # Topic fragment for building this topic with the parent topic

    general:
      Wh in kWh: true       # Automatically convert Wh to kWh
      republish after: 120  # Republish automatically after this time (if no other filter configured)

    inputs:
    - type: serial
      url: COM1   # Device path
      timeout: 3  # Seconds after which a timeout will be detected (default=3)
    - type: serial
      url: /dev/ttyS0   # Device path
      timeout: 3        # Seconds after which a timeout will be detected (default=3)

    devices:
      # Device configuration by reported id
      device_id_hex:

        mqtt:                           # Optional MQTT configuration for this meter.
          topic: DEVICE_BASE_TOPIC      # Topic fragment for building this topic with the parent topic

        status:                         # Optional MQTT status topic configuration for this meter
          topic: status                 # Topic fragment for building this topic with the parent topic

        skip:                           # OBIS codes (HEX) of values that will not be published (optional)
        - '00112233445566'

        # Configurations for each of the values (optional)
        values:

        - obis: '00112233445566'        # Obis code for this value
          mqtt:                         # Mqtt config for this value (optional)
            topic: OBIS_VALUE_TOPIC     # Topic fragment for building this topic with the topic prefix

          # A sequence of operations that will be evaluated one after another.
          # If one operation blocks nothing will be reported for this frame
          operations:
          - negative on energy meter status: true   # Make value negative based on an energy meter status. Set to "true" to enable or to "false" to disable workaround. If the default obis code for the energy meter is wrong set to the appropriate meter obis code instead
          - factor: 3   # Factor with which the value gets multiplied
          - offset: 100   # Offset that gets added on the value
          - round: 2   # Round to the specified digits
          # A sequence of operations that will be evaluated one after another.
          # The first value that gets returned by an operation will be used.
          - or:
            - type: change filter   # Filter which passes only changes
            - heartbeat filter: 120   # Filter which lets a value pass periodically every specified interval.


Configuration Reference
======================================
All possible configuration options are described here. Not all entries are created by default in the config file
and one should take extra care when changing those entries.

.. autopydantic_model:: sml2mqtt.config.config.Settings

logging
--------------------------------------

.. autopydantic_model:: sml2mqtt.config.logging.LoggingSettings
   :exclude-members: set_log_level

general
--------------------------------------

.. autopydantic_model:: sml2mqtt.config.config.GeneralSettings

inputs
--------------------------------------

.. autopydantic_model:: sml2mqtt.config.inputs.SerialSourceSettings
   :exclude-members: get_device_name

..
    YamlModel: sml2mqtt.config.inputs.SerialSourceSettings

.. code-block:: yaml

    type: serial
    url: COM3


.. autopydantic_model:: sml2mqtt.config.inputs.HttpSourceSettings
   :exclude-members: get_device_name

..
    YamlModel: sml2mqtt.config.inputs.HttpSourceSettings

.. code-block:: yaml

    type: http
    url: http://localhost:8080/sml
    interval: 3
    timeout: 10


mqtt
--------------------------------------

.. py:currentmodule:: sml2mqtt.config.mqtt

.. autopydantic_model:: MqttConfig

.. autopydantic_model:: MqttConnection

.. autopydantic_model:: OptionalMqttPublishConfig

.. autopydantic_model:: MqttDefaultPublishConfig

devices
--------------------------------------

.. py:currentmodule:: sml2mqtt.config.device

.. autopydantic_model:: SmlDeviceConfig

.. autopydantic_model:: SmlValueConfig
