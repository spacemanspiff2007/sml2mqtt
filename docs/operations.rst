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

    delta filter: 5

..
    YamlModel: DeltaFilter

.. code-block:: yaml

    delta filter: "5 %"


Heartbeat Filter
--------------------------------------

.. autopydantic_model:: HeartbeatFilter
   :inherited-members: BaseModel


Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..
    YamlModel: HeartbeatFilter

.. code-block:: yaml

    heartbeat filter: 60


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

Limit value
--------------------------------------

.. autopydantic_model:: LimitValue
   :inherited-members: BaseModel
   :exclude-members: type, get_kwargs_limit

Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..
    YamlModel: LimitValue

.. code-block:: yaml

    type: limit value
    min: 0


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
      - heartbeat filter: 60


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

This will report the power consumption of today

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
