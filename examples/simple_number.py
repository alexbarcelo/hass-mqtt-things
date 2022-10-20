#!/usr/bin/env python3
"""Example of the most simple usage of a Number instance.

The SimpleNumber is an OptimisticNumber that will appear on Home Assistant
and offers bidirectional control:

 - Home Assistant can set the value which triggers the call of the callback
 - Changes to the number are published to MQTT and thus updated on Home Assistant.
"""

from ham import MqttManager
from ham.number import OptimisticNumber
from time import sleep
import os

MQTT_USERNAME = os.environ["MQTT_USERNAME"]
MQTT_PASSWORD = os.environ["MQTT_PASSWORD"]
MQTT_HOST = os.environ["MQTT_HOST"]


class SimpleNumber(OptimisticNumber):
    name = "Awesomest Number"
    short_id = "moreawesome"

    def callback(self, state: float):
        super().callback(state)
        print("The number value is: %s" % state)

    def set_value(self, value: float):
        print("Setting value. Previous state: %f. New state: %f" % (self.state, value))
        self.state = value


if __name__ == "__main__":
    main_number = SimpleNumber()
    manager = MqttManager(MQTT_HOST, username=MQTT_USERNAME, password=MQTT_PASSWORD)
    manager.add_thing(main_number)

    manager.start()

    a = 1.1
    print("Entering an infinite loop, Ctrl+C multiple times to exit.")
    while True:
        sleep(5)
        if a >= 100:
            a -= 100
        main_number.set_value(a)
        a += 0.7
