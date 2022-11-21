#!/usr/bin/env python3
"""Example of how to trigger a reboot with a Button integration.

This script should be started by a user that has permissions for issuing
`systemctl reboot`.

I left an `echo` in front of the `systemctl reboot` command just to avoid
accidents. If you really want to reboot, just remove the echo.
"""

from ham import MqttManager
from ham.button import Button
from time import sleep
import os


MQTT_USERNAME = os.environ["MQTT_USERNAME"]
MQTT_PASSWORD = os.environ["MQTT_PASSWORD"]
MQTT_HOST = os.environ["MQTT_HOST"]


class RebootButton(Button):
    name = "Reboot button"
    short_id = "reboot_button"

    def callback(self):
        super().callback()
        os.system("echo systemctl reboot")


if __name__ == "__main__":
    reboot_button = RebootButton()
    manager = MqttManager(MQTT_HOST, username=MQTT_USERNAME, password=MQTT_PASSWORD)
    manager.add_thing(reboot_button)

    manager.start()

    print("Entering an infinite loop, Ctrl+C multiple times to exit.")
    while True:
        sleep(30)
