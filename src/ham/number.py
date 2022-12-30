from abc import abstractmethod

from .things import Thing
from .utils import WrapperCallback


class Number(Thing):
    """Basic class for a Number entity."""
    min: float
    max: float
    step: float

    config_fields = ["min", "max", "step"]

    _state: float = 1.0

    @property
    def component(self):
        return "number"

    @abstractmethod
    def callback(self, state: float):
        pass

    def raw_callback(self, topic, payload):
        value = float(payload)
        self._state = value
        return self.callback(value)

    def get_config(self):
        config = super().get_config()
        config["command_topic"] = f'~/{ self.short_id }/set'
        return config

    def set_callbacks(self):
        self.mqtt_manager.client.message_callback_add(
            f'{ self.mqtt_manager.base_topic }/{ self.short_id }/set',
            WrapperCallback(self.raw_callback)
        )


class OptimisticNumber(Number):
    """A Number that will track its state optimistically.

    "Optimistically" means that when the state is set (from Home Assistant or
    from the Python application) the number holds that value.
    """
    _state: float = 1

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        self.publish_state(self._state)

    def callback(self, state: float):
        self.state = state

    def get_config(self):
        config = super().get_config()
        config["state_topic"] = f'~/{ self.short_id }/main'
        return config
