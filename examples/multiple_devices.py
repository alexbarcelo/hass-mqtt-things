#!/usr/bin/env python3
"""Example of an application managing multiple devices.

This is a typical use case for bridges, in which a single hass-mqtt-things
application acts on behalf of more than one device.

This makes use of the optional DeviceInfo parameter on add_thing.
"""

from ham import MqttManager, DeviceInfo
from ham.switch import OptimisticSwitch
from time import sleep
import os

MQTT_USERNAME = os.environ["MQTT_USERNAME"]
MQTT_PASSWORD = os.environ["MQTT_PASSWORD"]
MQTT_HOST = os.environ["MQTT_HOST"]


class BaseSwitch(OptimisticSwitch):
    def __init__(self, index):
        self.index = index
        self.name = "switch %d" % index
        self.short_id = "s%d" % index

    def callback(self, state):
        print("The switch #%d has been set to %s" % (self.index, state))


if __name__ == "__main__":
    manager = MqttManager(MQTT_HOST, username=MQTT_USERNAME, password=MQTT_PASSWORD)
    all_switches = [BaseSwitch(200 + i) for i in range(3)]
    manager.add_things(all_switches)

    for device_id in range(3):
        switches = [BaseSwitch(100 + 10 * device_id + i) for i in range(3)]
        di = DeviceInfo(
            name="Device#%d" % device_id,
            hw_version="1.0.0alpha",
            sw_version="0.0.%dbeta" % device_id,
            identifiers=["device_testing_%02d" % device_id],
            connections=[("mac", "eb:%02d:de:c3:e5:f0" % device_id)],
        )
        manager.add_things(switches, origin=di)
        all_switches.extend(switches)

    manager.start()

    print("Entering an infinite loop, Ctrl+C multiple times to exit.")
    state = False
    while True:
        for s in all_switches:
            sleep(1)
            s.state = state
        state = not state
