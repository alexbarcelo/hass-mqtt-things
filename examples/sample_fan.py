#!/usr/bin/env python3
"""Example of the most simple usage of a Fan entity.

The Fan has five speeds.
"""

from ham import MqttManager
from ham.fan import PercentageOptimisticFan
from time import sleep
import os

MQTT_USERNAME = os.environ["MQTT_USERNAME"]
MQTT_PASSWORD = os.environ["MQTT_PASSWORD"]
MQTT_HOST = os.environ["MQTT_HOST"]


class SampleFan(PercentageOptimisticFan):
    name = "Awesomest Fan"
    short_id = "moreawesome"

    speed_range_min = 1
    speed_range_max = 5

    def callback(self, state: bool):
        super().callback(state)
        print("The fan is set to %s" % ("on" if state else "off",))

    def speed_callback(self, speed: int):
        super().speed_callback(speed)
        print("The fan is set to %s (received: %s)" % (self.speed, speed))

    def set_speed(self, speed: int):
        print("Setting value. Previous state: %d. New state: %d" % (self.speed, speed))
        self.speed = speed


if __name__ == "__main__":
    main_fan = SampleFan()
    manager = MqttManager(MQTT_HOST, username=MQTT_USERNAME, password=MQTT_PASSWORD)
    manager.add_thing(main_fan)

    manager.start()

    a = 1
    print("Entering an infinite loop, Ctrl+C multiple times to exit.")
    while True:
        sleep(5)
        if a > 5:
            a = 0
        main_fan.set_speed(a)
        a += 1
