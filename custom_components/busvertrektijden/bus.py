import aiohttp
from .const import API_URL


class BusStop:
    cancelled: bool


class Bus:
    def __init__(self, stop_name, short_name_filter, trip_headsign_filter):
        self.stop_name = stop_name
        self.short_name_filter = short_name_filter
        self.trip_headsign_filter = trip_headsign_filter
        self.ids = None

    async def get_next_buses(self):
        if self.ids == None:
            await self.get_ids()
        async with aiohttp.ClientSession() as session:
            url = f"{API_URL}/stops/{self.ids}?"
            if self.short_name_filter:
                url += f"shortnamefilter={self.short_name_filter}&"
            if self.trip_headsign_filter:
                url += f"tripheadsignfilter={self.trip_headsign_filter}"
            async with session.get(url) as response:
                data = await response.json()
                stopTimes = list(data['results'])[:10]
                return stopTimes

    async def get_ids(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/stops?q={self.stop_name}") as response:
                data = await response.json()
                stop = list(data['results'])[0]
                self.ids = ",".join(stop['ids'])
