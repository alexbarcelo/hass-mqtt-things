from threading import Thread
from typing import List

from getmac import get_mac_address
import paho.mqtt.client as mqtt
import json

import socket

from .things import Thing

from . import __version__


class MqttManager(Thread):
    things : List[Thing]
    client : mqtt.Client
    mqtt_host : str
    mqtt_port : int
    node_id : str
    base_topic : str
    name : str

    def __init__(self, host='localhost', port=1883, username=None, password=None,
                 *, node_id=None, base_topic=None, discovery_prefix='homeassistant',
                 name=None):
        """Initialize connection to the MQTT the server.
        
        This will prepare the MQTT connection using the provided configuration
        (host, port, username and password). By default, connection will be done
        to localhost:1883 without credentials.

        `node_id`, `base_topic` and `discovery_prefix` are optional parameters.
        If not specified, the hostname will be used for both `node_id` and 
        `base_topic` while the default 'homeassistant' will be used as the
        `discovery_prefix`.
        """
        super().__init__()

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        if username and password:
            self.client.username_pw_set(username, password=password)
        
        self.mqtt_host = host
        self.mqtt_port = port

        self.discovery_prefix = discovery_prefix
        
        # If node_id is not specified, the hostname will be used
        if node_id:
            self.node_id = node_id
        else:
            self.node_id = socket.gethostname()

        # If base_topic is not specified, the node_id will be used
        if base_topic:
            self.base_topic = base_topic
        else:
            self.base_topic = self.node_id

        # If name is not specified, use the node_id
        if name:
            self.name = name
        else:
            self.name = self.node_id

        self.things = list()

    def add_thing(self, thing : Thing):
        self.things.append(thing)
        thing.set_manager(self)

    def add_things(self, things: List[Thing]):
        self.things.extend(things)
        for thing in things:
            thing.set_manager(self)

    def run(self):
        print(f"Establishing connection to { self.mqtt_host }:{ self.mqtt_port }")
        self.client.connect(self.mqtt_host, self.mqtt_port)
        self.client.loop_forever()
    
    def on_message(self, _, userdata, msg):
        """React to a MQTT message.
        
        The derived class should reimplement this.
        """
        pass

    @staticmethod    
    def _format_mac(mac: str) -> str:
        """Format the mac address string for entry into dev reg.
        
        This has been taken from homeassistant/helpers/device_registry.py
        """
        to_test = mac

        if len(to_test) == 17 and to_test.count(":") == 5:
            return to_test.lower()

        if len(to_test) == 17 and to_test.count("-") == 5:
            to_test = to_test.replace("-", "")
        elif len(to_test) == 14 and to_test.count(".") == 2:
            to_test = to_test.replace(".", "")

        if len(to_test) == 12:
            # no : included
            return ":".join(to_test.lower()[i : i + 2] for i in range(0, 12, 2))

        # Not sure how formatted, return original
        return mac

    def get_mac(self) -> str:
        """Return the mac of this device.

        By default, this will use the getmac package.
        """
        return self._format_mac(get_mac_address())

    @property
    def availability_topic(self):
        return f"{ self.base_topic }/availability"

    @property
    def subscribe_topic(self):
        return f"{ self.base_topic }/+/set"

    def on_connect(self, _, userdata, flags, rc):
        print("Connected with result code %s" % rc)

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self.client.subscribe(self.subscribe_topic)

        common_config = {
            "~": self.base_topic,
            "availability_topic": self.availability_topic,
            "device": self._gen_device_info(),
        }

        for thing in self.things:
            config = thing.get_config()
            config.update(common_config)
            config["unique_id"] = f"{ self.get_mac() }_{ thing.short_id }"

            self.client.publish(
                f"{ self.discovery_prefix }/{ thing.component }/{ self.node_id }/{ thing.short_id }/config",
                json.dumps(config),
                retain=True
            )
            thing.set_callbacks()

        # Set up availability topic
        ###########################
        self.client.publish(self.availability_topic, "online", retain=True)
        self.client.will_set(self.availability_topic, "offline", retain=True)


    def _gen_device_info(self) -> dict:
        """Generate the device information payload."""
        mac_address = self.get_mac()
        return {
            "name": self.name,
            "identifiers": [f"{self.name}_{mac_address}"],
            "connections": [("mac", mac_address)],
            "sw_version": __version__,
        }
