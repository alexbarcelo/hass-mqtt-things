#!/usr/bin/env python3
"""Example of a dynamic instantiation of Switch instances.

The BaseSwitch is instantiated multiple times, and has an internal "index"
attribute. The main idea is that the application developer can use whatever
attributes or logic they need, and things can be dynamically instantiated.

One should not abuse, as the objects will have a unique_id and will persist
in Home Assistant. It is a good idea to have a deterministic way of generating
the `short_id`.
"""

from ham import MqttManager
from ham.switch import OptimisticSwitch
from time import sleep
import os

MQTT_USERNAME = os.environ["MQTT_USERNAME"]
MQTT_PASSWORD = os.environ["MQTT_PASSWORD"]
MQTT_HOST = os.environ["MQTT_HOST"]


class BaseSwitch(OptimisticSwitch):
    def __init__(self, index):
        self.index = index
        self.name = "Switch #%02d" % index
        self.short_id = "s%02d" % index

    def callback(self, state):
        print("The switch #%02d has been set to %s" % (self.index, state))


if __name__ == "__main__":
    switches = [BaseSwitch(i) for i in range(5)]
    manager = MqttManager(MQTT_HOST, username=MQTT_USERNAME, password=MQTT_PASSWORD)
    manager.add_things(switches)

    manager.start()

    print("Entering an infinite loop, Ctrl+C multiple times to exit.")
    state = False
    while True:
        for s in switches:
            sleep(1)
            s.state = state
        state = not state
