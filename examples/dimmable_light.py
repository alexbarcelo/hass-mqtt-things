"""Example of a the most simple usage of a Switch instance.

The SimpleLight is a DimmableLight that will appear on Home Assistant
and will illustrate how a simple optimistic dimmable light works.
"""

import os
from typing import Optional
from time import sleep

from ham import MqttManager
from ham.light import DimmableLight

MQTT_USERNAME = os.environ["MQTT_USERNAME"]
MQTT_PASSWORD = os.environ["MQTT_PASSWORD"]
MQTT_HOST = os.environ["MQTT_HOST"]


class SimpleLight(DimmableLight):
    name = "Dumbish Light"
    short_id = "dumbilight"

    def callback(self, *, state: bool, brightness: Optional[int] = None):
        if brightness is not None:
            print("The brightness is set to: %d" % brightness)
        print("State is set to: %s" % state)



if __name__ == "__main__":
    main_light = SimpleLight()
    manager = MqttManager(MQTT_HOST, username=MQTT_USERNAME, password=MQTT_PASSWORD)
    manager.add_thing(main_light)

    manager.start()

    print("Entering an infinite loop, Ctrl+C multiple times to exit.")
    while True:
        sleep(60)
