import logging
from collections import defaultdict
from threading import Thread
from typing import TypedDict, Optional

from getmac import get_mac_address
import paho.mqtt.client as mqtt
import json

import socket

from .things import Thing

from . import __version__


logger = logging.getLogger(__name__)

class DeviceInfo(TypedDict, total=False):
    configuration_url: str
    connections: list[tuple[str, str]]
    hw_version: str
    identifiers: list[str]
    manufacturer: str
    model: str
    name: str
    suggested_area: str
    sw_version: str
    via_device: str


class MqttManager(Thread):
    things: dict[Optional[DeviceInfo], list[Thing]]
    client: mqtt.Client
    node_id: str
    base_topic: str
    name: str
    unique_identifier: str

    def __init__(self, host='localhost', port=1883, username=None,
                 password=None, *, node_id=None, base_topic=None,
                 discovery_prefix='homeassistant', name=None,
                 unique_identifier=None):
        """Initialize connection to the MQTT the server.

        This will prepare the MQTT connection using the provided configuration
        (host, port, username and password). By default, connection will be
        done to localhost:1883 without credentials.

        `node_id`, `base_topic` and `discovery_prefix` are optional parameters.
        If not specified, the hostname will be used for both `node_id` and
        `base_topic` while the default 'homeassistant' will be used as the
        `discovery_prefix`.

        Setting `unique_identifier` is somewhat advanced. See:
        https://developers.home-assistant.io/docs/entity_registry_index 

        If you set the `unique_identifier`, it will be used for generating the
        unique_id for the Things. If not set, the mac of the device will be used
        (recommended). Set this ONLY if the MAC of the host is erratic (e.g. if
        you are using certain ARM single-board-computers that are MACless, 
        or if you are deploying into kubernetes).
        """
        super().__init__()

        logger.info("Initializing MqttManager; MQTT on %s:%s", host, port)

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        if username and password:
            logger.debug("Setting up authentication")
            self.client.username_pw_set(username, password=password)
        elif username or password:
            logger.warning("Misconfigured credentials, check that both username and password are set")

        # Asynchronous connect
        # which will not be made effective until the 
        # run() calls the .loop* method of the client
        self.client.connect_async(host, port)

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

        self.things = defaultdict(list)
        self.unique_identifier = unique_identifier or self.get_mac()
        self.device_info = self._gen_device_info()

        logger.debug("Initialization parameters: node_id=%s, base_topic=%s, discovery_prefix=%s, name=%s",
                     self.node_id, self.base_topic, self.discovery_prefix, self.name)

    def add_thing(self, thing: Thing, origin: Optional[DeviceInfo] = None):
        self.things[origin].append(thing)
        thing.set_manager(self)

    def add_things(self, things: list[Thing], origin: Optional[DeviceInfo] = None):
        self.things[origin].extend(things)
        for thing in things:
            thing.set_manager(self)

    def run(self):
        self.client.will_set(self.availability_topic, "offline", retain=True)
        logger.info("Starting MQTT client loop")
        self.client.loop_forever(retry_first_connection=True)

    def on_disconnect(self, _, userdata, rc):
        if rc != 0:
            logger.info("Unexpected MQTT disconnection (rc=%d).", rc)

    def on_message(self, _, userdata, msg):
        """React to a MQTT message.

        The derived class should reimplement this.
        """
        pass

    @staticmethod
    def _format_mac(mac: str) -> str:
        """Format the mac address string for entry into dev reg.

        This has been inspired by homeassistant/helpers/device_registry.py
        """
        to_test = mac

        if len(to_test) == 17 and to_test.count(":") == 5:
            return to_test.lower()

        to_test = to_test.replace("-", "")
        to_test = to_test.replace(".", "")

        if len(to_test) == 12:
            # no : included
            return ":".join(to_test.lower()[i:i + 2] for i in range(0, 12, 2))

        # Not sure how formatted, return original
        logger.warning("Not sure on the MAC, bypassing this: %s", mac)
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
        return [
            (f"{ self.base_topic }/+/set", 0),  # Most things use `set`
            (f"{ self.base_topic }/+/press", 0),  # Buttons use `press`
        ]

    def on_connect(self, _, userdata, flags, rc):
        logger.info("Connected with result code %d", rc)

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self.client.subscribe(self.subscribe_topic)

        logger.debug("Device information for this manager: %s", self.device_info)

        for origin, things in self.things.items():
            if origin is None:
                common_config = {
                    "~": self.base_topic,
                    "availability_topic": self.availability_topic,
                    "device": self.device_info,
                }
            else:
                common_config = {
                    "~": self.base_topic,
                    "availability_topic": self.availability_topic,
                    "device": origin,
                    "via": self.device_info["identifiers"][0]
                }

            for thing in things:
                logger.info("Publishing discovery message for: %r", thing)
                
                # New dictionary with sensible defaults
                config = common_config.copy()
                config["unique_id"] = f"{ self.unique_identifier }_{ thing.short_id }"

                # Then call get_config, and allow the implementation to override
                # the previously set defaults (at their own risk)
                config.update(thing.get_config())

                config_topic = "%s/%s/%s/%s/config" % (
                        self.discovery_prefix,
                        thing.component,
                        self.node_id,
                        thing.short_id
                    )

                logger.debug("Sending the following config dict to %s:\n%s", config_topic, config)

                self.client.publish(config_topic, json.dumps(config), retain=True)
                thing.set_callbacks()

        # Set up availability topic
        ###########################
        self.client.publish(self.availability_topic, "online", retain=True)

    def _gen_device_info(self) -> DeviceInfo:
        """Generate the device information payload."""
        return {
            "name": self.name,
            "identifiers": [f"{self.name}_{self.unique_identifier}"],
            "connections": [("mac", self.get_mac())],
            "sw_version": __version__,
        }
