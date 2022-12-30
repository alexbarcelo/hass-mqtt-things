from abc import abstractmethod

from .things import Thing
from .utils import WrapperCallback


class Switch(Thing):
    """Basic class for a Switch entity."""

    optimistic: bool

    config_fields = ["optimistic"]
    
    # The internal _state may or may not be used by the switch
    # (e.g. OptimisticSwitch relies on it, but ExplicitSwitch ignores it altogether)
    _state: bool = False

    @property
    def component(self):
        return "switch"

    @abstractmethod
    def callback(self, state: bool):
        pass

    def raw_callback(self, topic, payload):
        if payload == b'ON':
            self._state = True
            return self.callback(True)
        elif payload == b'OFF':
            self._state = False
            return self.callback(False)

    def get_config(self):
        config = super().get_config()
        config["command_topic"] = f'~/{ self.short_id }/set'
        return config

    def set_callbacks(self):
        self.mqtt_manager.client.message_callback_add(
            f'{ self.mqtt_manager.base_topic }/{ self.short_id }/set',
            WrapperCallback(self.raw_callback)
        )


class OptimisticSwitch(Switch):
    """A Switch that will track its state optimistically.

    "Optimistically" means that when the state is set (from Home Assistant or
    from the Python application) the switch becomes to that state.
    """
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


class ExplicitSwitch(Switch):
    """Track the state of the switch through explicit operations.

    This switch will only publish its state when the state attribute is
    explicitly set, and the callback is not implemented.

    It is a good idea to use this switch for mechanisms that have a somewhat
    slow or fuzzy cause/reaction flow. For example, a garage door may not be
    always working, and it is best to tie the state to a certain endstop and
    not to the activation trigger itself.
    """
    def _set_state(self, value: bool):
        self.publish_state(value)

    # This is a write-only property, as the state is not tracked at Home Assistant
    state = property(fset=_set_state)

    def get_config(self):
        config = super().get_config()
        config["state_topic"] = f'~/{ self.short_id }/main'
        return config


class StatelessSwitch(Switch):
    """A Switch that does not track its state.

    Home Assistant will not make any assumption regarding the state of this
    switch, and frontend will always allow to do the turn on and turn off
    operations.
    """
    # Currently, this is exactly the same as the base Switch class
    pass
