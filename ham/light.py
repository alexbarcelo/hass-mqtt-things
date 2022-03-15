from abc import abstractmethod
import json
from typing import Optional

from .things import Thing
from .utils import WrapperCallback


class Light(Thing):
    """Basic class for a Light entity.
    
    Internally, lights will also be done through JSON. Simple lights would not
    need that, but it makes it more modular and consistent across all supported
    lights in this library.
    """
    @property
    def component(self):
        return "light"

    @abstractmethod
    def callback(self, **kwargs):
        pass

    def raw_callback(self, topic, payload):
        self.callback(**json.loads(payload))

    def get_config(self):
        config = super().get_config()
        config["command_topic"] = f'~/{ self.short_id }/set'
        config["schema"] = "json"
        return config

    def set_callbacks(self):
        self.mqtt_manager.client.message_callback_add(
            f'{ self.mqtt_manager.base_topic }/{ self.short_id }/set',
            WrapperCallback(self.raw_callback)
        )


class DimmableLight(Light):
    BRIGHTNESS_SCALE = 255

    """An optimistic dimmable Light with no additional features."""
    def get_config(self):
        config = super().get_config()
        config["optimistic"] = True
        config["color_mode"] = True
        config["brightness"] = True
        config["brightness_scale"] = self.BRIGHTNESS_SCALE
        config["supported_color_modes"] = ["brightness"]
        return config

    @abstractmethod
    def callback(self, *, state: bool, brightness: Optional[int] = None):
        pass
