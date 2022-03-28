# sml2mqtt
[![Tests Status](https://github.com/spacemanspiff2007/sml2mqtt/workflows/Tests/badge.svg)](https://github.com/spacemanspiff2007/sml2mqtt/actions?query=workflow%3ATests)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sml2mqtt)](https://pypi.org/project/sml2mqtt/)
[![Updates](https://pyup.io/repos/github/spacemanspiff2007/sml2mqtt/shield.svg)](https://pyup.io/repos/github/spacemanspiff2007/sml2mqtt/)
[![PyPI](https://img.shields.io/pypi/v/sml2mqtt)](https://pypi.org/project/sml2mqtt/)
[![Downloads](https://pepy.tech/badge/sml2mqtt/month)](https://pepy.tech/project/sml2mqtt/month)

_A simple sml to mqtt bridge_


sml2mqtt is a asyncio application that can read multiple sml (Smart Message Language) streams
from energy meters and report the values through mqtt.

## Installation

Navigate to the folder where the virtual environment shall be created (e.g.).
```
cd /opt/sml2mqtt
```
If the folder does not exist yet you can create it with the ``mkdir`` command.


Create virtual environment (this will create a new subfolder "venv")::
```
python3 -m venv venv
```

Go into folder of virtual environment
```
cd venv
```

Activate the virtual environment
```
source bin/activate
```

Install sml2mqtt
```
python3 -m pip install --upgrade pip sml2mqtt
```


Run sml2mqtt
```
sml2mqtt --config PATH_TO_CONFIGURATION_FOLDER
```
A good configuration path would be ```/opt/sml2mqtt```.
sml2mqtt will automatically create a default configuration and a logfile there.

## Autostart

To automatically start the sml2mqtt from the virtual environment after a reboot call::
```
nano /etc/systemd/system/sml2mqtt.service
```

and copy paste the following contents. If the user/group which is running sml2mqtt is not "openhab" replace accordingly.
If your installation is not done in "/opt/sml2mqtt/venv/bin" replace accordingly as well::

```text
[Unit]
Description=sml2mqtt
Documentation=https://github.com/spacemanspiff2007/sml2mqtt
After=network-online.target

[Service]
Type=simple
User=openhab
Group=openhab
Restart=on-failure
RestartSec=2min
ExecStart=/opt/sml2mqtt/venv/bin/sml2mqtt -c PATH_TO_CONFIGURATION_FILE

[Install]
WantedBy=multi-user.target
```

Now execute the following commands to enable autostart::
```
sudo systemctl --system daemon-reload
sudo systemctl enable sml2mqtt.service
```

It is now possible to start, stop, restart and check the status of sml2mqtt with::
```
sudo systemctl start sml2mqtt.service
sudo systemctl stop sml2mqtt.service
sudo systemctl restart sml2mqtt.service
sudo systemctl status sml2mqtt.service
```

## Analyze

Starting sml2mqtt with the ``-a`` or ``--analyze`` arg will analyze a single sml frame and report the output.
It's a convenient way to check what values will be reported.
It will also show how the configuration changes the sml values (e.g. if you add a transformation or a workaround).

```
sml2mqtt --config PATH_TO_CONFIGURATION_FOLDER -a
```
Output
```
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
```

## Configuration

Configuration is done in the ``config.yml`` file.
It is possible to create a default configuration. Just use the ``-c`` command line switch and specify a path to load
the configuration from. If the file does not exist a sample file will be created.

```yml
logging:
  level: INFO                    # Log level
  file: sml2mqtt.log             # Log file path (absolute or relative to config file)

mqtt:
  connection:
    client id: sml2mqtt
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
ports:
- url: COM1
  timeout: 3
- url: /dev/ttyS0
  timeout: 3


devices:
  # Device configuration by OBIS value 0100000009ff or by url if the device does not report OBIS 0100000009ff
  11111111111111111111:
    mqtt:
      topic: DEVICE_TOPIC

    # OBIS IDs that will not be processed (optional)
    skip:
    - OBIS
    - values
    - to skip

    # Configuration how each OBIS value is reported. Create as many OBIS IDs (e.g. 0100010800ff as you like).
    # Each sub entry (mqtt, workarounds, transformations, filters) is optional and can be omitted
    values:

      OBIS:
        # Sub topic how this value is reported.
        mqtt:
          topic: OBIS

        # Workarounds allow the enabling workarounds (e.g. if the device has strange behaviour)
        # These are the available workarounds
        workarounds:
        - negative on energy meter status: true   # activate this workaround

        # Transformations allow mathematical calculations on the obis value
        # They are applied in order how they are defined
        transformations:
        - factor: 3     # multiply with factor
        - offset: 100   # add offset
        - round: 2      # round on two digits

        # Filters control how often a value is published over mqtt.
        # If one filter is true the value will be published
        filters:
        - diff: 10      # report if value difference is >= 10
        - perc: 10      # report if percentage change is >= 10%
        - every: 120    # report at least every 120 secs (overrides the value from general)
```


### Example devices configuration
One energy meter is connected to the serial port. The serial meter reports OSIB ``0100000009ff``
as ``11111111111111111111``.

For this device
- the mqtt topic fragment is set to ``light``
- the value ``0100010801ff`` will not be published
- The following values of the device are specially configured:

  - Energy value (OBIS ``0100010800ff``)
    - Will be rounded to one digit
    - Will be published on change **or** at least every hour
    - The mqtt topic used is ``sml2mqtt/light/energy``

  - Power value (OBIS ``0100100700ff``)
    - Will be rounded to one digit
    - Will be published if at least a 5% power change occurred **or** at least every 2 mins
      (default from ``general`` -> ``republish after``)
    - The mqtt topic used is ``sml2mqtt/light/power``


```yaml
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
```
