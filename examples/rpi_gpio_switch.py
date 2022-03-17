#!/usr/bin/env python3
"""Example of how to expose a GPIO of a Raspberry Pi to Home Assistant.

This script should have direct access to the GPIO of the Raspberry (we assume
that the script is running in the RPi itself). So that justifies the use of an
optimistic switch.

This example uses the library RPi.GPIO. But the main idea can be used with any
similar library, and even different boards with different GPIO capabilities.

In addition to being controlled through Home Assistant (and receiving the update
through the callback method) changes on the switch can be triggered through
Python itself.
"""

from ham import MqttManager
from ham.switch import OptimisticSwitch
from time import sleep
import os

import RPi.GPIO as GPIO

MQTT_USERNAME = os.environ["MQTT_USERNAME"]
MQTT_PASSWORD = os.environ["MQTT_PASSWORD"]
MQTT_HOST = os.environ["MQTT_HOST"]

GPIO_PIN = os.environ["GPIO_PIN"]


class GPIOSwitch(OptimisticSwitch):
    name = "GPIO Switch"
    short_id = "gpioswitch"

    def __init__(self, pin):
        super().__init__()
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)

    def callback(self, state: bool):
        super().callback(state)
        if state:
            GPIO.output(self.pin, GPIO.HIGH)
        else:
            GPIO.output(self.pin, GPIO.LOW)


if __name__ == "__main__":
    GPIO.setmode(GPIO.BOARD)
    main_switch = GPIOSwitch(GPIO_PIN)
    manager = MqttManager(MQTT_HOST, username=MQTT_USERNAME, password=MQTT_PASSWORD)
    manager.add_thing(main_switch)

    manager.start()

    print("Entering an infinite loop, Ctrl+C multiple times to exit.")
    while True:
        sleep(30)
        # Auto switches on every 30 seconds
        main_switch.state = True
