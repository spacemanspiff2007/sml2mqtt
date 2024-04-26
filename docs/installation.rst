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

Stable release (currently 2.2)
------------------------------

Installation through `docker <https://hub.docker.com/r/spacemanspiff2007/sml2mqtt>`_ is available:

.. code-block:: bash

    docker pull spacemanspiff2007/sml2mqtt:latest


The docker image has one volume ``/sml2mqtt`` which has to be mounted.
There the ``config.yml`` will be used or a new ``config.yml`` will be created

The analyze option can also be set through an environment variable
(see :ref:`command line interface <COMMAND_LINE_INTERFACE>`).

Easiest way to run a docker with a locally mounted volume:

.. code-block:: bash

    mkdir sml2mqtt
    docker run  -v $(pwd)/sml2mqtt:/sml2mqtt spacemanspiff2007/sml2mqtt:latest
    # This will quit after a few seconds (with an error on the logs at sml2mqtt/sml2mqtt.log)
    vi sml2mqtt/config.yml
    # Edit the config according to your needs
    docker run  -v $(pwd)/sml2mqtt:/sml2mqtt spacemanspiff2007/sml2mqtt:latest
    # This schould now continue running, check with
    docker ps

Building the docker image from source
-------------------------------------

First you need to create a fresh docker image, then it is mostly similar to the above.

.. code-block:: bash

    cd ~
    mkdir GIT
    cd GIT
    git clone https://github.com/spacemanspiff2007/sml2mqtt.git
    cd sml2mqtt
    docker built -t sml2mqtt .
    cd ~
    mkdir -p dockerdata/sml2mqtt
    cd dockerdata
    docker run  -v $(pwd)/sml2mqtt:/sml2mqtt sml2mqtt

    # This will quit after a few seconds (with an error on the logs at 
    # sml2mqtt/sml2mqtt.log)
    # Now edit the config according to your needs and start again
    vi sml2mqtt/config.yml    
    docker run -v $(pwd)/sml2mqtt:/sml2mqtt sml2mqtt
    
    # This should now not return an error and if everything runs for a minute 
    # interrupt it with Ctrl-C and start the container in detached mode
    docker run -d -v $(pwd)/sml2mqtt:/sml2mqtt sml2mqtt

    # Check if it is running
    docker ps -a

You can further adjust the config to process the values and restart docker...