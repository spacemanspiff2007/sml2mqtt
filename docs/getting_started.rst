**************************************
Getting started
**************************************

First install ``sml2mqtt`` e.g in a :ref:`virtual environment <INSTALLATION_VENV>`.

Run ``sml2mqtt`` with a path to a configuration file.
A new default configuration file will be created.

Edit the configuration file and add the serial ports.

Now run ``sml2mqtt`` with the path to the configuration file and the ``analyze`` option.
(see :ref:`command line interface <COMMAND_LINE_INTERFACE>`).
This will process one sml frame from the meter and report the output.
It's a convenient way to check what values will be reported.
It will also show how the configuration changes the sml values (e.g. if you add a transformation or a workaround).

Example output for the meter data:

.. code-block:: text

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


Check if the meter reports the serial number unter obis``0100000009ff``.
If not it's possible to configure another number for configuration matching.
If yes replace ``SERIAL_ID_HEX`` in the dummy configuration with the reported
serial number (here ``11111111111111111111``).
Modify the device configuration to your liking.
Run the analyze command again and see how the output changes and observe the reported values.
