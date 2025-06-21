**************************************
Installation
**************************************

Virtual environment
======================================

.. _INSTALLATION_VENV:

Installation
--------------------------------------

.. hint::
   On Windows use the ``python`` command instead of ``python3``


Navigate to the folder in which the virtual environment shall be created (e.g.)::

    cd /opt/sml2mqtt

If the folder does not exist yet you can create it with the ``mkdir`` command::

    mkdir /opt/sml2mqtt


Create virtual environment (this will create a new subfolder "venv")::

    python3 -m venv venv


Go into folder of virtual environment::

    cd venv


#. Activate the virtual environment

   Linux::

    source bin/activate

   Windows::

    Scripts\activate

#. Upgrade pip and setuptools::

    python3 -m pip install --upgrade pip setuptools

Install sml2mqtt::

    python3 -m pip install sml2mqtt

#. Run sml2mqtt::

    sml2mqtt --config PATH_TO_CONFIGURATION_FILE


Upgrading
--------------------------------------
#. Stop sml2mqtt

#. Activate the virtual environment

    Navigate to the folder where sml2mqtt is installed::

        cd /opt/sml2mqtt

    Activate the virtual environment

    Linux::

        source bin/activate

    Windows::

        Scripts\activate

#. Run the following command in your activated virtual environment::

    python3 -m pip install --upgrade sml2mqtt

#. Start sml2mqtt

#. Observe the log for errors in case there were changes


Autostart after reboot
--------------------------------------

To automatically start the sml2mqtt from the virtual environment after a reboot call::

    nano /etc/systemd/system/sml2mqtt.service


and copy paste the following contents. If the user/group which is running sml2mqtt is not "openhab" replace accordingly.
If your installation is not done in "/opt/sml2mqtt/venv/bin" replace accordingly as well::

    [Unit]
    Description=sml2mqtt
    Documentation=https://github.com/spacemanspiff2007/sml2mqtt
    After=network-online.target

    [Service]
    Type=simple
    User=openhab
    Group=openhab
    Restart=on-failure
    RestartSec=10min
    ExecStart=/opt/sml2mqtt/venv/bin/sml2mqtt -c PATH_TO_CONFIGURATION_FILE

    [Install]
    WantedBy=multi-user.target


Now execute the following commands to enable autostart::

    sudo systemctl --system daemon-reload
    sudo systemctl enable sml2mqtt.service


It is now possible to start, stop, restart and check the status of sml2mqtt with::

    sudo systemctl start sml2mqtt.service
    sudo systemctl stop sml2mqtt.service
    sudo systemctl restart sml2mqtt.service
    sudo systemctl status sml2mqtt.service

Docker
======================================

The application is available as Docker image ``spacemanspiff2007/sml2mqtt`` via `Docker Hub <https://hub.docker.com/r/spacemanspiff2007/sml2mqtt>`_.

Installation
--------------------------------------

#. Create a ``compose.yml`` containing a data directory and the location of your serial device. Example:

    .. literalinclude:: ../compose.example.yml
        :language: yaml

    The subdirectory ``./data`` is mounted as Docker volume. An existing ``config.yml`` will be used, otherwise a new ``config.yml`` will be created.

#. Start sml2mqtt
    * As background service::

        docker compose up -d sml2mqtt

    * One-shot with analyze option::

        docker compose run -e SML2MQTT_ANALYZE=1 --rm sml2mqtt


Upgrading
--------------------------------------
#. Stop sml2mqtt::

    docker compose down

#. Update the Docker image::

    docker compose pull

#. Start sml2mqtt::

    docker compose up -d

#. Observe the log for errors in case there were changes


Autostart after reboot
--------------------------------------

To automatically start sml2mqtt after a reboot, add ``restart: unless-stopped`` to your ``compose.yml``.
