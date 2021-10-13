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
RestartSec=60s
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
It's convenient way to check what values will be reported.

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

```yml
logging:
  level: INFO
  file: /opt/sml2mqtt/sml2mqtt.log

mqtt:
  connection:
    client_id: sml2mqtt
    host: localhost
    port: 1883
    user: ''
    password: ''
    tls: false
    tls_insecure: false
  publish:
    qos: 0        # Default QoS when publishing values
    retain: false # Default retain flag when publishing values
  topics:
    base topic: sml2mqtt  # Topic that will prefix all topics
    last will: status     # Last will topic

    # These aliases are replaced in the mqtt topics
    alias:
      0100010800ff: total_energy

# Configuration of the sml devices
devices:
- device: COM24
  timeout: 3        # Timeout in seconds between messages from the device
  skip:
  - value ids that will
  - not be reported

general:
  max wait: 120  # Time in seconds sml2mqtt waits for a value change until the value gets republished
```