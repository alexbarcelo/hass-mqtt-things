"""Example of a the most simple usage of a Switch instance.

The SimpleSwitch is an OptimisticSwitch that will appear on Home Assistant
and offers bidirectional control:

 - Home Assistant can set the state and the callback code is called
   (as shown below in method `callback`)
 - Changes to the switch state (as shown in the `toggle` method) are published
   to MQTT and thus updated on Home Assistant.
"""

from ham import MqttManager
from ham.switch import OptimisticSwitch
from time import sleep
import os

MQTT_USERNAME = os.environ["MQTT_USERNAME"]
MQTT_PASSWORD = os.environ["MQTT_PASSWORD"]
MQTT_HOST = os.environ["MQTT_HOST"]

class SimpleSwitch(OptimisticSwitch):
    name = "Awesomest Switch"
    short_id = "moreawesome"

    def callback(self, state: bool):
        super().callback(state)
        print("The switch state is: %s" % state)

    def toggle(self):
        print("Toggling state. Previous state: %s" % self.state)
        self.state = not self.state
        print("Toggling state. Next state: %s" % self.state)


if __name__ == "__main__":
    main_switch = SimpleSwitch()
    manager = MqttManager(MQTT_HOST, username=MQTT_USERNAME, password=MQTT_PASSWORD)
    manager.add_thing(main_switch)

    manager.start()

    print("Entering an infinite loop, Ctrl+C multiple times to exit.")    
    while True:
        sleep(5)
        main_switch.toggle()
