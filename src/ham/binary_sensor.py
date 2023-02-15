import logging

from .things import Thing

logger = logging.getLogger(__name__)


class BinarySensor(Thing):
    """Basic class for a Binary Sensor entity.
    
    Binary Sensors are things that only publish an ON or OFF state.

    This is implemented in this library through a write-only property, called
    `state`. Other Sensor subclasses may reimplement them; the responsible of
    publishing stuff is the Thing.publish_state method.
    """
    device_class: str
    enabled_by_default: bool
    encoding: str
    entity_category: str
    expire_after: int
    force_update: bool
    icon: str

    config_fields = [
        "device_class", "enabled_by_default", "encoding", "entity_category",
        "expire_after", "force_update", "icon"
    ]

    @property
    def component(self):
        return "binary_sensor"

    @property
    def state(self):
        raise AttributeError("Canonical implementation of binary_sensor has a write-only state")

    @state.setter
    def state(self, value: bool):
        self.publish_state(value)

    def get_config(self):
        config = super().get_config()
        config["state_topic"] = f'~/{ self.short_id }/main'
        return config
