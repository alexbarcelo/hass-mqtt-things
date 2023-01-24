#!/usr/bin/env python3
"""Example of how to add attributes to any entity.

In this particular example, a Sensor entity will be used. The main mechanisms
can be used for all Things.

The sensor is useless and nonsensical. But it should illustrate the difference
between setting the state and setting the attributes.
"""

from ham import MqttManager
from ham.sensor import Sensor
from time import sleep
import os


MQTT_USERNAME = os.environ["MQTT_USERNAME"]
MQTT_PASSWORD = os.environ["MQTT_PASSWORD"]
MQTT_HOST = os.environ["MQTT_HOST"]


class UserIDSensor(Sensor):
    name = "UserID"
    short_id = "uid"


if __name__ == "__main__":
    uid_sensor = UserIDSensor()
    manager = MqttManager(MQTT_HOST, username=MQTT_USERNAME, password=MQTT_PASSWORD)
    manager.add_thing(uid_sensor)

    manager.start()

    print("Entering an infinite loop, Ctrl+C multiple times to exit.")
    while True:
        uid_sensor.state = os.getuid()
        uid_sensor.attributes = {"posix_name": os.getlogin()}
        sleep(30)
