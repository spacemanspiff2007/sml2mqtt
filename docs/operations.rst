.. py:currentmodule:: sml2mqtt.config.operations


**************************************
Operations
**************************************

It's possible to define operations which are used to process the received value



Filters
======================================


Change Filter
--------------------------------------

.. autopydantic_model:: OnChangeFilter
   :exclude-members: get_kwargs_on_change
   :inherited-members: BaseModel

Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..
    YamlModel: OnChangeFilter

.. code-block:: yaml

    type: change filter


Range filter
--------------------------------------

.. autopydantic_model:: RangeFilter
   :inherited-members: BaseModel
   :exclude-members: type, get_kwargs_limit

Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..
    YamlModel: RangeFilter

.. code-block:: yaml

    type: range filter
    min: 0


Delta Filter
--------------------------------------

.. autopydantic_model:: DeltaFilter
   :exclude-members: get_kwargs_delta
   :inherited-members: BaseModel

Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..
    YamlModel: DeltaFilter

.. code-block:: yaml

    type: delta filter
    min: 5
    min %: 10

..
    YamlModel: DeltaFilter

.. code-block:: yaml

    type: delta filter
    min: 5

..
    YamlModel: DeltaFilter

.. code-block:: yaml

    type: delta filter
    min %: 10


Throttle Filter
--------------------------------------

.. autopydantic_model:: ThrottleFilter
   :inherited-members: BaseModel


Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..
    YamlModel: ThrottleFilter

.. code-block:: yaml

    throttle filter: 60


Actions
======================================


Refresh Action
--------------------------------------

.. autopydantic_model:: RefreshAction
   :inherited-members: BaseModel


Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..
    YamlModel: RefreshAction

.. code-block:: yaml

    refresh action: 01:30:00


Heartbeat Action
--------------------------------------

.. autopydantic_model:: HeartbeatAction
   :inherited-members: BaseModel


Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..
    YamlModel: HeartbeatAction

.. code-block:: yaml

    heartbeat action: 30

Math
======================================


Factor
--------------------------------------

.. autopydantic_model:: Factor
   :inherited-members: BaseModel


Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..
    YamlModel: Factor

.. code-block:: yaml

    factor: -1


Offset
--------------------------------------

.. autopydantic_model:: Offset
   :inherited-members: BaseModel


Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..
    YamlModel: Offset

.. code-block:: yaml

    offset: 10

Round
--------------------------------------

.. autopydantic_model:: Round
   :inherited-members: BaseModel

Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..
    YamlModel: Round

.. code-block:: yaml

    round: 2


Workarounds
======================================


Negative On Energy Meter Status
--------------------------------------

.. autopydantic_model:: NegativeOnEnergyMeterWorkaround
   :inherited-members: BaseModel


Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..
    YamlModel: NegativeOnEnergyMeterWorkaround

.. code-block:: yaml

    negative on energy meter status: true


Date time based
======================================


Virtual Meter
--------------------------------------

.. autopydantic_model:: VirtualMeter
   :inherited-members: BaseModel
   :exclude-members: get_kwargs_dt_fields, type


Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..
    YamlModel: VirtualMeter

.. code-block:: yaml

    type: meter
    start now: False
    reset times:
      - 02:00
    reset days:
      - 1
      - monday


Max Value
--------------------------------------

.. autopydantic_model:: MaxValue
   :inherited-members: BaseModel
   :exclude-members: get_kwargs_dt_fields, type


Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..
    YamlModel: MaxValue

.. code-block:: yaml

    type: max value
    start now: True
    reset times:
      - 02:00


Min Value
--------------------------------------

.. autopydantic_model:: MinValue
   :inherited-members: BaseModel
   :exclude-members: get_kwargs_dt_fields, type


Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..
    YamlModel: MinValue

.. code-block:: yaml

    type: min value
    start now: True
    reset times:
      - 02:00


Time series
======================================



Max Value
--------------------------------------

.. autopydantic_model:: MaxOfInterval
   :inherited-members: BaseModel
   :exclude-members: get_kwargs_interval_fields, type


Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..
    YamlModel: MaxOfInterval

.. code-block:: yaml

    type: max interval
    interval: 3600
    wait for data: False


Min Value
--------------------------------------

.. autopydantic_model:: MinOfInterval
   :inherited-members: BaseModel
   :exclude-members: get_kwargs_interval_fields, type


Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..
    YamlModel: MinOfInterval

.. code-block:: yaml

    type: min interval
    interval: 3600
    wait for data: False


Mean Value
--------------------------------------

.. autopydantic_model:: MeanOfInterval
   :inherited-members: BaseModel
   :exclude-members: get_kwargs_interval_fields, type


Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..
    YamlModel: MeanOfInterval

.. code-block:: yaml

    type: mean interval
    interval: 3600
    wait for data: False


Operations
======================================


Or
--------------------------------------

.. autopydantic_model:: Or
   :inherited-members: BaseModel


Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..
    YamlModel: Or

.. code-block:: yaml

    or:
      - type: change filter
      - heartbeat action: 60


Sequence
--------------------------------------

.. autopydantic_model:: Sequence
   :inherited-members: BaseModel


Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..
    YamlModel: Sequence

.. code-block:: yaml

    sequence:
      - factor: 0.1
      - offset: -50



Examples
======================================
.. py:currentmodule:: sml2mqtt.config.device

These are some examples for sml value configurations

Energy consumption today
--------------------------------------

This will report the power consumption of today.
The first reported value every day will be 0 and then it will increase for every day.

..
    YamlModel: SmlValueConfig

.. code-block:: yaml

    obis: '0100010800ff'    # Obis code for the energy meter
    mqtt:
      topic: energy_today   # MQTT topic for the meter
    operations:
    - type: meter
      start now: true       # Start immediately
      reset times:          # Reset at midnight
        - 00:00
    - round: 1
    - type: change filter      # Only report on changes
    - refresh action: 01:00    # ... but refresh every hour


Downsample current power
--------------------------------------

This will report a power value every max every 30s.
The reported value will be the weighted mean value of the last 30s.

..
    YamlModel: SmlValueConfig

.. code-block:: yaml

    obis: '0100100700ff'    # Obis code for the energy meter
    mqtt:
      topic: power   # MQTT topic for the meter
    operations:
    - type: mean interval     # Calculate weighted mean over 30s
      interval: 30
      wait for data: False
    - throttle filter: 30     # Let a value pass every 30s
    - round: 0                # Round the mean value to the full number
    - type: delta filter      # Only report when the value changes at least 10W or 5%
      min: 10
      min %: 5
    - refresh action: 01:00   # ... but refresh every hour


Home Assistant MQTT Sensors
--------------------------------------

This will add MQTT Sensors to `Home Assistant <https://www.home-assistant.io/>`_. One can add this to a `package <https://www.home-assistant.io/docs/configuration/packages/>`_.

.. code-block:: yaml

   mqtt:
     sensor:
       - name: "sml01_energy_total"
         unique_id: f855b69a-828b-4cad-bafd-7563a909153e
         state_topic: "sml2mqtt/sml01/energy_total"
         icon: mdi:transmission-tower
         unit_of_measurement: kWh
         state_class: total
         device_class: energy
         availability:
           topic: "sml2mqtt/status"
           payload_available: "ONLINE"
           payload_not_available: "OFFLINE"
       - name: "sml01_energy_total_returned"
         unique_id: 855b9e06-9d39-41e9-afc0-ee0f567aacb2
         state_topic: "sml2mqtt/sml01/energy_total_returned"
         icon: mdi:transmission-tower
         unit_of_measurement: kWh
         state_class: total
         device_class: energy
         availability:
           topic: "sml2mqtt/status"
           payload_available: "ONLINE"
           payload_not_available: "OFFLINE"
         operations:
           refresh action: 24:00
       - name: "sml01_momentary_power"
         unique_id: 5ddc1f63-bd73-4d9b-86a1-3e7dfeccee1e
         state_topic: "sml2mqtt/sml01/momentary_power"
         unit_of_measurement: W
         state_class: measurement
         device_class: power
         availability:
           topic: "sml2mqtt/status"
           payload_available: "ONLINE"
           payload_not_available: "OFFLINE"
       - name: "sml01_real_power_l1"
         unique_id: 3db5879a-a810-41cf-9489-359d9486948c
         state_topic: "sml2mqtt/sml01/real_power_l1"
         unit_of_measurement: W
         state_class: measurement
         device_class: power
         availability:
           topic: "sml2mqtt/status"
           payload_available: "ONLINE"
           payload_not_available: "OFFLINE"
       - name: "sml01_real_power_l2"
         unique_id: cd12d5ff-4662-483f-8744-7cf44e171ccc
         state_topic: "sml2mqtt/sml01/real_power_l2"
         unit_of_measurement: W
         state_class: measurement
         device_class: power
         availability:
           topic: "sml2mqtt/status"
           payload_available: "ONLINE"
           payload_not_available: "OFFLINE"
       - name: "sml01_real_power_l3"
         unique_id: d9f37985-65d8-46c8-84c6-c8588e589d62
         state_topic: "sml2mqtt/sml01/real_power_l3"
         unit_of_measurement: W
         state_class: measurement
         device_class: power
         availability:
           topic: "sml2mqtt/status"
           payload_available: "ONLINE"
           payload_not_available: "OFFLINE"
       - name: "sml01_voltage_l1"
         unique_id: 05ab47a3-3c91-4de1-afe6-af3efd10852a
         state_topic: "sml2mqtt/sml01/voltage_l1"
         unit_of_measurement: W
         state_class: measurement
         device_class: voltage
         availability:
           topic: "sml2mqtt/status"
           payload_available: "ONLINE"
           payload_not_available: "OFFLINE"
       - name: "sml01_voltage_l2"
         unique_id: 694fb3cd-b9b7-4d08-821a-abaa7766cc76
         state_topic: "sml2mqtt/sml01/voltage_l2"
         unit_of_measurement: W
         state_class: measurement
         device_class: voltage
         availability:
           topic: "sml2mqtt/status"
           payload_available: "ONLINE"
           payload_not_available: "OFFLINE"
       - name: "sml01_voltage_l3"
         unique_id: b6595e49-c7d9-491e-8947-855e61c987ae
         state_topic: "sml2mqtt/sml01/voltage_l3"
         unit_of_measurement: W
         state_class: measurement
         device_class: voltage
         availability:
           topic: "sml2mqtt/status"
           payload_available: "ONLINE"
           payload_not_available: "OFFLINE"
