import logging
from typing import Union

from .things import Thing

logger = logging.getLogger(__name__)


class Sensor(Thing):
    """Basic class for a Sensor entity.
    
    Sensor are things that only publish their state (they have no callback).

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
    state_class: str
    unit_of_measurement: str

    config_fields = [
        "device_class", "enabled_by_default", "encoding", "entity_category",
        "expire_after", "force_update", "icon", "state_class",
        "unit_of_measurement"
    ]

    @property
    def component(self):
        return "sensor"

    @property
    def state(self):
        raise AttributeError("Canonical implementation of sensor has a write-only state")

    @state.setter
    def state(self, value: Union[bool, bytes, str, int, float]):
        self.publish_state(value)

    def get_config(self):
        config = super().get_config()
        config["state_topic"] = f'~/{ self.short_id }/main'
        return config
