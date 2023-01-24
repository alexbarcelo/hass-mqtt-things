from abc import ABCMeta, abstractmethod
import json
from typing import Union, TYPE_CHECKING, ClassVar, Any

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
        ret["json_attributes_topic"] = f'~/{ self.short_id }/attrs'
        return ret

    def set_callbacks(self):
        """Establish the callbacks for this Thing.

        This method typically involves several calls to Client.message_callback_add.
        """
        pass

    def publish_mqtt_message(self, payload: bytes, substate: str):
        self.mqtt_manager.client.publish(
            f'{ self.mqtt_manager.base_topic }/{ self.short_id }/{ substate }',
            payload
        )

    def publish_state(self, state: Union[bool, bytes, str, int, float]):
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

        self.publish_mqtt_message(payload, "main")

    @property
    def attributes(self):
        raise AttributeError("Attributes is write-only by design")

    @attributes.setter
    def attributes(self, attributes: Any):
        """Publish the JSON attributes of this entity."""
        self.publish_mqtt_message(bytes(json.dumps(attributes), "utf-8"), "attrs")

    def __repr__(self) -> str:
        return f"<{ self.__class__.__name__ } thing name={ self.name }, id={ self.short_id }>"
