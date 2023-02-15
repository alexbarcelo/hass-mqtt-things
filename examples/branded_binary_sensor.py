#!/usr/bin/env python3
"""Example of a binary sensor with some device branding."""

from ham import MqttManager
from ham.binary_sensor import BinarySensor
from time import sleep
import os

MQTT_USERNAME = os.environ["MQTT_USERNAME"]
MQTT_PASSWORD = os.environ["MQTT_PASSWORD"]
MQTT_HOST = os.environ["MQTT_HOST"]


class IsTurnedOn(BinarySensor):
    name = "Is this turned on?"
    short_id = "turned_on"


if __name__ == "__main__":
    bs = IsTurnedOn()
    manager = MqttManager(MQTT_HOST, username=MQTT_USERNAME, password=MQTT_PASSWORD)
    manager.device_info["manufacturer"] = "AwesomeM"
    manager.device_info["model"] = "ScrapPilePC"

    manager.add_thing(bs)

    manager.start()

    print("Entering an infinite loop, Ctrl+C multiple times to exit.")
    while True:
        sleep(5)
        bs.state = True
