**************************************
Getting started
**************************************

1. Installation
======================================

First install ``sml2mqtt`` e.g in a :ref:`virtual environment <INSTALLATION_VENV>`.

2. Create default configuration
======================================

Run ``sml2mqtt`` with a path to a configuration file.
A new default configuration file will be created.

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
          - factor: 3               # Factor with which the value gets multiplied
          - offset: 100             # Offset that gets added on the value
          - round: 2                # Round to the specified digits
          - refresh action: 300     # Republish value every 300s

3. Edit inputs and mqtt
======================================

Edit the configuration file and configure the appropriate :ref:`inputs <CONFIG_INPUTS>` for
serial or http (e.g. for tibber) and edit the mqtt settings.


..
    YamlModel: Settings

.. code-block:: yaml
   :linenos:
   :emphasize-lines: 8-11, 26-31


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
          - factor: 3               # Factor with which the value gets multiplied
          - offset: 100             # Offset that gets added on the value
          - round: 2                # Round to the specified digits
          - refresh action: 300     # Republish value every 300s


4. Run with analyze
======================================

Now run ``sml2mqtt`` with the path to the configuration file and the ``--analyze`` option.
(see :ref:`command line interface <COMMAND_LINE_INTERFACE>`).
This will process one sml frame from the meter and report the output.
It's a convenient way to check what values will be reported.
It will also show how the configuration changes the reported values when you add an operation.

Check if the meter reports the serial number unter obis ``0100000009ff``.
Example output for the meter data:

.. code-block:: text
   :emphasize-lines: 33, 38

    SmlMessage
        transaction_id: 17c77d6b
        group_no      : 0
        abort_on_error: 0
        message_body <SmlOpenResponse>
            codepage   : None
            client_id  : None
            req_file_id: 07ed29cd
            server_id  : 11111111111111111111
            ref_time   : None
            sml_version: None
        crc16         : 25375
    SmlMessage
        transaction_id: 17c77d6c
        group_no      : 0
        abort_on_error: 0
        message_body <SmlGetListResponse>
            client_id       : None
            sever_id        : 11111111111111111111
            list_name       : 0100620affff
            act_sensor_time : 226361515
            val_list: list
                <SmlListEntry>
                    obis           : 8181c78203ff
                    status         : None
                    val_time       : None
                    unit           : None
                    scaler         : None
                    value          : ISK
                    value_signature: None
                    -> (Hersteller-Identifikation)
                <SmlListEntry>
                    obis           : 0100000009ff
                    status         : None
                    val_time       : None
                    unit           : None
                    scaler         : None
                    value          : 11111111111111111111
                    value_signature: None
                    -> (Geräteeinzelidentifikation)
                <SmlListEntry>
                    obis           : 0100010800ff
                    status         : 386
                    val_time       : None
                    unit           : 30
                    scaler         : -1
                    value          : 123456789
                    value_signature: None
                    -> 12345678.9Wh (Zählerstand Total)
                <SmlListEntry>
                    obis           : 0100010801ff
                    status         : None
                    val_time       : None
                    unit           : 30
                    scaler         : -1
                    value          : 123456789
                    value_signature: None
                    -> 12345678.9Wh (Zählerstand Tarif 1)
                <SmlListEntry>
                    obis           : 0100010802ff
                    status         : None
                    val_time       : None
                    unit           : 30
                    scaler         : -1
                    value          : 0
                    value_signature: None
                    -> 0.0Wh (Zählerstand Tarif 2)
                <SmlListEntry>
                    obis           : 0100100700ff
                    status         : None
                    val_time       : None
                    unit           : 27
                    scaler         : 0
                    value          : 555
                    value_signature: None
                    -> 555W (aktuelle Wirkleistung)
                <SmlListEntry>
                    obis           : 8181c78205ff
                    status         : None
                    val_time       : None
                    unit           : None
                    scaler         : None
                    value          : XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
                    value_signature: None
                    -> (Öffentlicher Schlüssel)
            list_signature  : None
            act_gateway_time: None
        crc16         : 22117
    SmlMessage
        transaction_id: 17c77d6d
        group_no      : 0
        abort_on_error: 0
        message_body <SmlCloseResponse>
            global_signature: None
        crc16         : 56696


If the meter does not report ``0100000009ff`` it's possible to configure another number (of even multiple ones)
for configuration matching (see :ref:`command line interface <CONFIG_GENERAL>`).

5. Edit device settings
======================================

Replace ``device_id_hex`` in the dummy configuration with the reported number (here ``11111111111111111111``).
Edit the mqtt settings or remove them to use the default. Add the obis code of values that should not be reported
to the skip section. Run the analyze command again to see how the reported values change.

..
    YamlModel: Settings

.. code-block:: yaml
   :linenos:
   :emphasize-lines: 13, 15-16, 18-19, 21-22

    # ...

    inputs:
    - type: serial
      url: COM1   # Device path
      timeout: 3  # Seconds after which a timeout will be detected (default=3)
    - type: serial
      url: /dev/ttyS0   # Device path
      timeout: 3        # Seconds after which a timeout will be detected (default=3)

    devices:
      # Device configuration by reported id
      '11111111111111111111':

        mqtt:                           # Optional MQTT configuration for this meter.
          topic: meter_light            # Topic fragment for building this topic with the parent topic

        status:                         # Optional MQTT status topic configuration for this meter
          topic: status                 # Topic fragment for building this topic with the parent topic

        skip:                           # OBIS codes (HEX) of values that will not be published (optional)
        - '8181c78205ff'

        # Configurations for each of the values (optional)
        values:

        - obis: '00112233445566'        # Obis code for this value
          mqtt:                         # Mqtt config for this value (optional)
            topic: OBIS_VALUE_TOPIC     # Topic fragment for building this topic with the topic prefix
          # A sequence of operations that will be evaluated one after another.
          # If one operation blocks nothing will be reported for this frame
          operations:
          - negative on energy meter status: true   # Make value negative based on an energy meter status. Set to "true" to enable or to "false" to disable workaround. If the default obis code for the energy meter is wrong set to the appropriate meter obis code instead
          - factor: 3               # Factor with which the value gets multiplied
          - offset: 100             # Offset that gets added on the value
          - round: 2                # Round to the specified digits
          - refresh action: 300     # Republish value every 300s


6. Edit value settings
======================================

It's possible to further configure how values will be reported.
For every value there are multiple operations that can be applied.
Each sml value can also be processed multiple times.

Run the analyze command again to see how the reported values change.

..
    YamlModel: Settings

.. code-block:: yaml
   :linenos:
   :emphasize-lines: 27-37, 39-45, 47-52

    # ...

    inputs:
    - type: serial
      url: COM1   # Device path
      timeout: 3  # Seconds after which a timeout will be detected (default=3)
    - type: serial
      url: /dev/ttyS0   # Device path
      timeout: 3        # Seconds after which a timeout will be detected (default=3)

    devices:
      # Device configuration by reported id
      '11111111111111111111':

        mqtt:                           # Optional MQTT configuration for this meter.
          topic: meter_light            # Topic fragment for building this topic with the parent topic

        status:                         # Optional MQTT status topic configuration for this meter
          topic: status                 # Topic fragment for building this topic with the parent topic

        skip:                           # OBIS codes (HEX) of values that will not be published (optional)
        - '8181c78205ff'

        # Configurations for each of the values (optional)
        values:

        -  obis: '0100010800ff'    # Obis code for the energy value
           mqtt:
             topic: energy_today
           operations:
           - type: meter
             start now: true       # Start immediately
             reset times:          # Reset at midnight
               - 00:00
           - round: 1
           - type: change filter      # Only report on changes
           - refresh action: 01:00    # ... but refresh every hour

        -  obis: '0100010800ff'  # Obis code for the energy value
           mqtt:
             topic: energy_total
           operations:
           - round: 1
           - type: change filter
           - refresh action: 01:00

        -  obis: '0100100700ff'  # Obis code for the power value
           mqtt:
             topic: power
           operations:
           - delta filter: 5%
           - refresh action: 01:00


Output from the analyze command that shows what values will be reported

.. code-block:: text

   ...
   sml2mqtt/meter_light/energy_today: 0 (QOS: 0, retain: False)
   sml2mqtt/meter_light/energy_total: 12345.7 (QOS: 0, retain: False)
   sml2mqtt/meter_light/power: 555 (QOS: 0, retain: False)
   sml2mqtt/meter_light/status: OK (QOS: 0, retain: False)
   ...
