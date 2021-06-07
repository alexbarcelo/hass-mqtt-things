from abc import ABCMeta, abstractmethod


class Thing(metaclass=ABCMeta):
    name: str
    short_id: str

    @property
    @abstractmethod
    def component(self):
        pass

    def set_manager(self, mqtt_manager):
        self.mqtt_manager = mqtt_manager

    def get_config(self):
        return {
            "name": self.name
        }

    def set_callbacks(self):
        """Establish the callbacks for this Thing.
        
        This method typically involves several calls to Client.message_callback_add.
        """
        pass

    def publish_state(self, state, substate='main'):
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
