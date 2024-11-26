# sml2mqtt
[![Tests Status](https://github.com/spacemanspiff2007/sml2mqtt/workflows/Tests/badge.svg)](https://github.com/spacemanspiff2007/sml2mqtt/actions?query=workflow%3ATests)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sml2mqtt)](https://pypi.org/project/sml2mqtt/)
[![PyPI](https://img.shields.io/pypi/v/sml2mqtt)](https://pypi.org/project/sml2mqtt/)
[![Downloads](https://pepy.tech/badge/sml2mqtt/month)](https://pepy.tech/project/sml2mqtt)
[![Docker Image Version (latest by date)](https://img.shields.io/docker/v/spacemanspiff2007/sml2mqtt?label=docker)](https://hub.docker.com/r/spacemanspiff2007/sml2mqtt)
[![Docker Pulls](https://img.shields.io/docker/pulls/spacemanspiff2007/sml2mqtt)](https://hub.docker.com/r/spacemanspiff2007/sml2mqtt)

_A simple yet extremely flexible sml to mqtt bridge_


sml2mqtt is a asyncio application that can read multiple sml (Smart Message Language) streams
from energy meters and report the values through mqtt.
The meters can be read through serial ports or through http(s) (e.g. Tibber devices)

To read from the serial port an IR to USB reader for energy meter is required.

# Documentation
[The documentation can be found at here](https://sml2mqtt.readthedocs.io)


# Changelog

#### 3.3 (2024-11-26)
- Updated dependencies and docs
- Allow rounding to the tenth

#### 3.2 (2024-11-05)
- Automatically select CRC e.g. for Holley DTZ541

#### 3.1 (2024-08-05)
- Updated dependencies
- Added some small log messages

#### 3.0 (2024-04-24)

**BREAKING CHANGE**

- Almost complete rewrite, requires at least **Python 3.10**
- Extensive value processing which can be configured -> **Config file changed**
- Support for tibber pulse out of the box
- The ``analyze`` flag can also be set through an environment variable which makes it easier for docker users

#### 2.2 (2023-03-31)
- Small config improvements

#### 2.1 (2023-03-27)
- Additional obis id for serial number matching
- Improved serial reading a bit

#### 2.0.0 (2023-03-22)
- Release rework
