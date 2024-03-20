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
      level: INFO                    # Log level
      file: sml2mqtt.log             # Log file path (absolute or relative to config file)

    mqtt:
      connection:
        identifier: sml2mqtt
        host: localhost
        port: 1883
        user: ''
        password: ''
        tls: false
        tls insecure: false

      # MQTT default configuration
      # All other topics use these values if no other values for qos/retain are set
      # It's possible to override
      #  - topic        (fragment that is used to build the full mqtt topic)
      #  - full_topic   (will not build the topic from the fragments but rather use the configured value)
      #  - qos
      #  - retain
      # for each (!) mqtt-topic entry
      defaults:
        qos: 0
        retain: false
      topic prefix: sml2mqtt

      last will:
        topic: status

    general:
      Wh in kWh: true                  # Automatically convert Wh to kWh
      republish after: 120             # Republish automatically after this time (if no other every filter is configured)

    # Serial port configurations for the sml readers
    inputs:
    - url: COM1
      timeout: 3
    - url: /dev/ttyS0
      timeout: 3


    devices:
      # Device configuration by OBIS value 0100000009ff or by url if the device does not report OBIS 0100000009ff
      '11111111111111111111':
        mqtt:
          topic: DEVICE_TOPIC

        # OBIS IDs that will not be processed (optional)
        skip:
        - '112233445566'
        - '778899AABBCC'

        # Configuration how each OBIS value is reported. Create as many entries as you like.
        # It's even possible to process a value multiple times (e.g. to report a daily max value)
        values:

          - obis: '112233445566'
            # Sub topic how this value is reported (Optional).
            mqtt:
              topic: OBIS
            # optional, leave if you do not want to process the raw value
            operations:
              - negative on energy meter status: true   # activate this workaround
              - factor: 3                               # multiply with factor
              - offset: 100                             # add offset
              - round: 2                                # round on two digits


Example devices
--------------------------------------
One energy meter is connected to the serial port. The serial meter reports OBIS ``0100000009ff``
as ``11111111111111111111``.

For this device

* the mqtt topic fragment is set to ``light``
* the value ``0100010801ff`` will not be published
* The following values of the device are specially configured:

  * Energy value (OBIS ``0100010800ff``)

    * Will be rounded to one digit
    * Will be published on change **or** at least every hour
    * The mqtt topic used is ``sml2mqtt/light/energy``.
      (Built through ``topic prefix`` + ``device mqtt`` + ``value mqtt``)


  * Power value (OBIS ``0100100700ff``)

    * Will be rounded to one digit
    * Will be published if at least a 5% power change occurred **or** at least every 2 mins
      (default from ``general`` -> ``republish after``)
    * The mqtt topic used is ``sml2mqtt/light/power``


.. code-block:: yaml

    devices:
      11111111111111111111:
        mqtt:
          topic: light
        skip:
        - 0100010801ff
        values:
          0100010800ff:
            mqtt:
              topic: energy
            transformations:
            - round: 1
            filters:
            - every: 3600
          0100100700ff:
            mqtt:
              topic: power
            filters:
            - perc: 5


Configuration Reference
======================================
All possible configuration options are described here. Not all entries are created by default in the config file
and one should take extra care when changing those entries.

.. autopydantic_model:: sml2mqtt.config.config.Settings

logging
--------------------------------------

.. autopydantic_model:: sml2mqtt.config.logging.LoggingSettings

general
--------------------------------------

.. autopydantic_model:: sml2mqtt.config.config.GeneralSettings

ports
--------------------------------------

.. autopydantic_model:: sml2mqtt.config.source.SerialSourceSettings

.. autopydantic_model:: sml2mqtt.config.source.HttpSourceSettings

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
