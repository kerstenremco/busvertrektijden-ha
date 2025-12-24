from homeassistant import config_entries
from .const import DOMAIN, CONF_STOP_NAME, API_URL
import voluptuous as vol
import aiohttp

SEARCH_SCHEMA = vol.Schema({
    vol.Required('search'): str
})


class BusVertrektijdenConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Bus vertrektijden config flow."""

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=SEARCH_SCHEMA, errors=errors
            )

        # User has submitted the stop_name, validate it
        search_query = user_input['search']
        stops = await self._get_stops(search_query)
        if not stops or len(stops) == 0:
            # No stops found, show error and re-prompt
            errors['search'] = f"Halte niet gevonden. Probeer opnieuw."
            return self.async_show_form(
                step_id="user",
                data_schema=SEARCH_SCHEMA, errors=errors
            )

        # Stops found, proceed to select stop step
        SELECT_STOP_SCHEMA = vol.Schema({
            vol.Required("selected_stop"): vol.In(stops)
        })
        return self.async_show_form(
            step_id="select_stop",
            data_schema=SELECT_STOP_SCHEMA,
            errors=errors,
            description_placeholders={
                "example": "Select a stop from the list."}
        )

    async def _get_stops(self, query: str):
        """Fetch stops from the API."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/stops?q={query}") as response:
                data = await response.json()
                stopTimes = dict({"redo": "-- Zoek opnieuw --"})
                for item in data['results']:
                    name = item['name']
                    stopTimes[name] = name
                return stopTimes

    async def async_step_select_stop(self, user_input=None):
        """Final step: user selected a stop_id, create the entry."""
        name = user_input["selected_stop"]
        if name == "redo":
            return await self.async_step_user()

        return self.async_create_entry(
            title=name,
            data={CONF_STOP_NAME: name},
        )
