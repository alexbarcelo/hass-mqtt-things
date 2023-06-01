from abc import abstractmethod
import logging

from .things import Thing
from .utils import WrapperCallback

logger = logging.getLogger(__name__)


class Fan(Thing):
    """Basic class for a Fan entity.
    
    Fan entities can have quite a lot of behavior (oscillation, direction, 
    presets...). For now, fans only consider the speed, set through a single
    `command_topic`.
    """
    optimistic: bool
    speed_range_max: int
    speed_range_min: int

    config_fields = ["optimistic", "speed_range_max", "speed_range_min"]

    _state: bool = False
    _speed: int  # Used only for fans with speed

    @property
    def component(self):
        return "fan"

    @abstractmethod
    def callback(self, state: bool):
        pass

    def raw_callback(self, topic, payload):
        print("Here: %s %s" % (topic, payload))
        if payload == b'ON':
            self._state = True
            return self.callback(True)
        elif payload == b'OFF':
            self._state = False
            return self.callback(False)
        else:
            logger.warning("Ignoring unrecognized command: `%s`", payload)

    def get_config(self):
        config = super().get_config()
        config["command_topic"] = f'~/{ self.short_id }/set'
        return config

    def set_callbacks(self):
        self.mqtt_manager.client.message_callback_add(
            f'{ self.mqtt_manager.base_topic }/{ self.short_id }/set',
            WrapperCallback(self.raw_callback)
        )


class BinaryOptimisticFan(Fan):
    """A fan that tracks its own on/off state."""
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value: bool):
        self._state = value
        self.publish_state(self._state)

    def callback(self, state: bool):
        self.state = state

    def get_config(self):
        config = super().get_config()
        config["state_topic"] = f'~/{ self.short_id }/main'
        return config


class PercentageOptimisticFan(BinaryOptimisticFan):
    """A Fan that has regulable speed."""

    speed_range_min = 1
    speed_range_max = 100
    _speed = 1

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value: int):
        if value == 0:
            self.state = False
            # don't touch the _speed, it works as the "last known speed"
        else:
            self.state = True

            self._speed = value
            self.publish_mqtt_message(bytes(str(value), "utf-8"), "speed/state")
            self.publish_state(self._state)

    def speed_callback(self, speed: int):
        self.speed = speed

    def raw_speed_callback(self, topic: str, raw_speed: bytes):
        print("Hey!")
        self.speed_callback(int(raw_speed.decode("utf-8")))

    def get_config(self):
        config = super().get_config()
        config["percentage_state_topic"] = f'~/{ self.short_id }/speed/state'
        config["percentage_command_topic"] = f'~/{ self.short_id }/speed/set'
        return config

    def set_callbacks(self):
        super().set_callbacks()        
        self.mqtt_manager.client.message_callback_add(
            f'{ self.mqtt_manager.base_topic }/{ self.short_id }/speed/set',
            WrapperCallback(self.raw_speed_callback)
        )
