from homeassistant import config_entries
from .const import DOMAIN, CONF_STOP_NAME, CONF_SHORT_NAME_FILTER, API_URL
import voluptuous as vol
import aiohttp


def normalize_commas(value: str | None) -> str | None:
    if value is None:
        return None
    return ",".join(part.strip() for part in value.strip().split(","))


class BusVertrektijdenConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Bus vertrektijden config flow."""
    VERSION = 1

    def __init__(self):
        self._search_query: str | None = None
        self._stops: dict[str] | None = None
        self._selected_stop: str | None = None
        self._short_name_filter: str | None = None

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            self._search_query = user_input['search']
            await self._get_stops()
            if self._stops and len(self._stops) > 1:
                return await self.async_step_select_stop()
            else:
                errors['search'] = "Halte niet gevonden. Probeer opnieuw."

        SEARCH_SCHEMA = vol.Schema({
            vol.Required('search'): str
        })

        return self.async_show_form(
            step_id="user",
            data_schema=SEARCH_SCHEMA,
            errors=errors
        )

    async def _get_stops(self):
        """Fetch stops from the API."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/stops?search={self._search_query}") as response:
                data = await response.json()
                stopTimes = dict({"redo": "-- Zoek opnieuw --"})
                for item in data['result']:
                    name = item['stop_name']
                    stopTimes[name] = name
                self._stops = stopTimes

    async def async_step_select_stop(self, user_input=None):
        """Final step: user selects a stop from the list."""

        if user_input is None:
            return self.async_show_form(
                step_id="select_stop",
                data_schema=vol.Schema({
                    vol.Required("selected_stop"): vol.In(self._stops)
                })
            )

        selected_stop = user_input["selected_stop"]
        if selected_stop == "redo":
            return await self.async_step_user()
        else:
            self._selected_stop = selected_stop
            return await self.async_step_filters()

    async def async_step_filters(self, user_input=None):
        """Optional step: user sets filters for short name"""
        if user_input is None:
            return self.async_show_form(
                step_id="filters",
                data_schema=vol.Schema({
                    vol.Optional("short_name_filter"): str
                })
            )

        self._short_name_filter = normalize_commas(
            user_input.get("short_name_filter"))
        return self.async_create_entry(
            title=self._selected_stop,
            data={CONF_STOP_NAME: self._selected_stop, CONF_SHORT_NAME_FILTER: self._short_name_filter})
