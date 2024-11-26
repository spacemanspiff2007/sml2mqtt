**************************************
Smart Home Systems
**************************************

Here are some examples to get started with various smart home systems.
They all still require some changes so make sure to modify them to fit your setup.

openHAB
======================================

Integration for `openHAB <https://www.openhab.org/>`_ requires that the
`MQTT Binding <https://www.openhab.org/addons/bindings/mqtt.generic/>`_ is used.
The example connects through the Bridge ``mqtt:broker:localhost``

| The topics you enter under ``stateTopic`` must match the topics you have configured in the sml2mqtt configuration.
| Run sml2mqtt with the ``-a`` or ``--analyze`` flag to see the topics that are being published.

.. code-block:: text
   :caption: .things file

   Thing mqtt:topic:stromzaehler "Stromzähler" (mqtt:broker:localhost) [
           availabilityTopic="stromzaehler/status", payloadAvailable="ONLINE", payloadNotAvailable="OFFLINE"
       ]
   {
       Channels:

       Type number : leistung          [stateTopic="stromzaehler/leistung",   unit="W"]
       Type number : energie           [stateTopic="stromzaehler/energie",   unit="kWh"]
       ...


       Type string : status            [stateTopic="stromzaehler/status"]
   }

.. code-block:: text
   :caption: .items file

   String          Zuhause_Status     "Status [%s]"         {channel="mqtt:topic:stromzaehler:status"}
   Number:Power    Zuhause_Leistung   "Leistung [%d W]"     {channel="mqtt:topic:stromzaehler:leistung",  unit="W", expire="5m"}
   Number:Energy   Zuhause_Energie    "Energie [%.2f kWh]"  {channel="mqtt:topic:stromzaehler:leistung",  unit="kWh"}


HomeAssistant
======================================

Integration for `Home Assistant <https://www.home-assistant.io/>`_  requires that the
`mqtt integration <https://www.home-assistant.io/integrations/mqtt#configuration>`_ is used.

| The topics you enter under ``state_topic`` and ``topic`` must match the topics you have
  configured in the sml2mqtt configuration.
| Run sml2mqtt with the ``-a`` or ``--analyze`` flag to see the topics that are being published.

.. code-block:: yaml

   mqtt:
     sensor:
       - name: "sml2mqtt_energy_total"
         unique_id: f955b69a-828b-4cad-bafd-7563a909153e
         state_topic: "sml2mqtt/meter1/energy_total"
         icon: mdi:transmission-tower
         unit_of_measurement: kWh
         state_class: total
         device_class: energy
         availability:
           topic: "sml2mqtt/status"
           payload_available: "ONLINE"
           payload_not_available: "OFFLINE"

       - name: "sml2mqtt_momentary_power"
         unique_id: 6ddc1f63-bd73-4d9b-86a1-3e7dfeccee1e
         state_topic: "sml2mqtt/meter1/momentary_power"
         unit_of_measurement: W
         state_class: measurement
         device_class: power
         availability:
           topic: "sml2mqtt/status"
           payload_available: "ONLINE"
           payload_not_available: "OFFLINE"

       ...
