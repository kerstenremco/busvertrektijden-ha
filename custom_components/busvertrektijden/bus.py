import aiohttp
from .const import API_URL


class BusStop:
    cancelled: bool


class Bus:
    def __init__(self, stop_name, short_name_filter):
        self.stop_name = stop_name
        self.short_name_filter = short_name_filter

    async def get_next_buses(self):
        async with aiohttp.ClientSession() as session:
            url = f"{API_URL}/stop/{self.stop_name.lower()}?"
            if self.short_name_filter:
                url += f"filternumbers={self.short_name_filter}"
            async with session.get(url) as response:
                data = await response.json()
                stopTimes = list(data['result']['stop_times'])[:10]
                return stopTimes
