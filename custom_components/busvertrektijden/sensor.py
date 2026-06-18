import logging
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from .const import CONF_STOP_NAME, CONF_SHORT_NAME_FILTER
from datetime import timedelta
from .bus import Bus

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=1)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_STOP_NAME): cv.string,
    vol.Optional(CONF_SHORT_NAME_FILTER): cv.string,
})


async def async_setup_entry(hass, entry, async_add_entities):
    # Add sensors here
    config = entry.data
    sensors = []
    short_name_filter = config.get(
        CONF_SHORT_NAME_FILTER) if CONF_SHORT_NAME_FILTER in config else None
    bus = Bus(config[CONF_STOP_NAME], short_name_filter)
    sensors.append(StopSensor(bus))
    async_add_entities(sensors, update_before_add=True)


class StopSensor(Entity):
    def __init__(self, bus: Bus):
        super().__init__()
        self._bus = bus
        self._state = 0
        self._stops = []
        self._available = True

    @property
    def name(self):
        return f"Bus Stop {self._bus.stop_name}"

    @property
    def unique_id(self):
        return self._bus.stop_name

    @property
    def available(self):
        return self._available and self._bus.stop_name is not None

    @property
    def should_poll(self):
        return True

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return {
            "stops": self._stops
        }

    async def async_update(self):
        # Fetch new state data for the sensor
        try:
            stops = await self._bus.get_next_buses()
            self._state = stops[0]['seconds'] if stops else 0
            self._stops = stops
            self._available = True
        except Exception as e:
            _LOGGER.error(f"Fout bij ophalen data: {e}")
            self._available = False
