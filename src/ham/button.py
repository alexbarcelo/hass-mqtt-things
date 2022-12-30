import logging
from abc import abstractmethod

from .things import Thing
from .utils import WrapperCallback

logger = logging.getLogger(__name__)


class Button(Thing):
    """Basic class for a Button entity."""
    @property
    def component(self):
        return "button"

    @abstractmethod
    def callback(self):
        pass

    def raw_callback(self, topic, payload):
        if payload == b"PRESS":
            return self.callback()
        else:
            logger.warning("%r Received an unknown payload: '%s'. Ignoring", self, payload)

    def get_config(self):
        config = super().get_config()
        config["command_topic"] = f'~/{ self.short_id }/press'

        logger.debug("%r Command topic set to: %s", self, config["command_topic"])
        return config

    def set_callbacks(self):
        self.mqtt_manager.client.message_callback_add(
            f'{ self.mqtt_manager.base_topic }/{ self.short_id }/press',
            WrapperCallback(self.raw_callback)
        )
