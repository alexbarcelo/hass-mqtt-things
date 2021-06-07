[![PyPI version](https://badge.fury.io/py/hass-mqtt-things.svg)](https://pypi.org/project/hass-mqtt-things/)

# Home Assistant MQTT Things

Library for rapid development of things to be integrated with Home Assistant through MQTT

## Demo/quickstart

If you have a Home Assistant instance reachable, and have a MQTT in place, you can easily
use this library and the examples to show how to proceed.

A quick way of starting is:

```bash
$ git clone https://github.com/alexbarcelo/hass-mqtt-things.git
$ cd hass-mqtt-things
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -e .
$ export MQTT_HOST="hassio.local"
$ export MQTT_USERNAME="user"
$ export MQTT_PASSWORD="password"
$ cd examples
$ python interactive_switch.py
```

Of course, you will need to change the `export` lines and adapt them to your MQTT
setup (host/username/password).

Once you have followed the above steps, a new _Awesomest Switch_ should have appeared
and it will toggle every 5 seconds.

## More examples

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

At this moment only the Switch is done. But, eventually, I plan to add all devices that are supported
by the MQTT Discovery mechanism.

