from abc import ABCMeta, abstractmethod
from typing import Union, TYPE_CHECKING, ClassVar

# LiteralString is from Python 3.11;
# atm, we want to support Python 3.9
try:
    from typing import LiteralString
except ImportError:
    LiteralString = str

if TYPE_CHECKING:
    from ham.manager import MqttManager


class Thing(metaclass=ABCMeta):
    name: str
    short_id: str
    mqtt_manager: "MqttManager"

    config_fields: ClassVar[list[LiteralString]] = []

    @property
    @abstractmethod
    def component(self):
        pass

    def set_manager(self, mqtt_manager: "MqttManager"):
        self.mqtt_manager = mqtt_manager

    def get_config(self) -> dict[str, Union[int, float, str]]:
        ret = dict()

        for config_field_name in self.config_fields:
            if hasattr(self, config_field_name):
                ret[config_field_name] = getattr(self, config_field_name)

        ret["name"] = self.name
        return ret

    def set_callbacks(self):
        """Establish the callbacks for this Thing.

        This method typically involves several calls to Client.message_callback_add.
        """
        pass

    def publish_state(self, state: Union[bool, bytes, str, int, float], substate='main'):
        """Set the state of this entity.

        If use_state_topic attribute is True, then calling this method will
        publish the state of the switch.
        """
        if state is True:
            payload = b'ON'
        elif state is False:
            payload = b'OFF'
        elif isinstance(state, bytes):
            payload = state
        else:
            payload = bytes(str(state), "UTF-8")

        self.mqtt_manager.client.publish(
            f'{ self.mqtt_manager.base_topic }/{ self.short_id }/{ substate }',
            payload
        )

    def __repr__(self) -> str:
        return f"<{ self.__class__.__name__ } thing name={ self.name }, id={ self.short_id }>"
