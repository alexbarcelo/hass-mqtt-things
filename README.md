# Home Assistant MQTT Things

[![PyPI version](https://badge.fury.io/py/hass-mqtt-things.svg)](https://pypi.org/project/hass-mqtt-things/)

Python library for rapid integration of Things with Home Assistant through MQTT.

## Demonstration

If you have a Home Assistant instance reachable, and have a MQTT in place
(with discovery activated), you can easily use this library and the provided
examples show you how to proceed.

### From the source code

A quick way of starting from scratch (by cloning this project and creating a
virtual environment) is shown below:

```bash
$ git clone https://github.com/alexbarcelo/hass-mqtt-things.git
Cloning into 'hass-mqtt-things'...
remote: Enumerating objects: (...)
(...)
$ cd hass-mqtt-things
$ python3 -m venv venv
$ source venv/bin/activate
(venv)$ pip install --upgrade pip
Collecting pip
  (...)
Installing collected packages: pip
  (...)
(venv)$ pip install -e .
Obtaining file:(...)
(...)
Successfully installed getmac-0.8.3 hass-mqtt-things-0.3.0 paho-mqtt-1.6.1
(venv)$ export MQTT_HOST="hassio.local"
(venv)$ export MQTT_USERNAME="user"
(venv)$ export MQTT_PASSWORD="password"
(venv)$ cd examples
(venv)$ ./interactive_switch.py
Entering an infinite loop, Ctrl+C multiple times to exit.
Connected with result code 0
Toggling state. Previous state: False
Toggling state. Next state: True
(... ad infinitum)
```

NOTE: I have put an explicit upgrade for the `pip` package because I am using the "new"
setup.cfg approach, which doesn't work with certain old versions.

You will need to change the `export` lines and adapt them to your MQTT setup
(set up your host, username and password information).

Once you have followed the above steps, a new _Awesomest Switch_ should have appeared
and it will toggle every 5 seconds.

### With PyPI packages

Assuming you are in a proper environment (e.g. a Python _virtual environment_)
you can easily install this package and try a demo from the `examples` folder:

```bash
$ pip install hass-mqtt-things
Collecting hass-mqtt-things
  Downloading hass_mqtt_things-0.2.0-py3-none-any.whl (10 kB)
(...)
Successfully installed getmac-0.8.3 hass-mqtt-things-0.2.0 paho-mqtt-1.6.1
$ curl -O https://raw.githubusercontent.com/alexbarcelo/hass-mqtt-things/main/examples/interactive_switch.py
$ export MQTT_HOST="hassio.local"
$ export MQTT_USERNAME="user"
$ export MQTT_PASSWORD="password"
$ chmod +x interactive_switch.py
$ ./interactive_switch.py
Entering an infinite loop, Ctrl+C multiple times to exit.
Connected with result code 0
Toggling state. Previous state: False
Toggling state. Next state: True
(... ad infinitum)
```

You will need to change the `export` lines and adapt them to your MQTT setup
(set up your host, username and password information).

Once you have followed the above steps, a new _Awesomest Switch_ should have appeared
and it will toggle every 5 seconds.

### More examples

Check the [examples folder](examples). You will find some more examples there.

## Use cases

This library is aimed to Python developers that are using Home Assistant for their
home automation projects and wants to be more agile in their deployment. The foundation
for this project is the [MQTT Discovery](https://www.home-assistant.io/docs/mqtt/discovery/)
mechanism of Home Assistant.

Some use cases where this library can become handy:

- GPIO control for a Raspberry Pi.
- Monitor something on your desktop PC (temperature, mount points, whether a certain application is running...).
- Management of serial connections (for example: video projectors with serial input).
- Alarm control panels on a Raspberry Pi.

At this moment both the Switch and Light component are done. I plan to add all
devices that are supported by the MQTT Discovery mechanism, but my personal use
cases will drive the roadmap (unless there are Pull Requests or specific
petitions in this repository).
