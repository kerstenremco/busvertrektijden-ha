import aiohttp
from .const import API_URL


class BusStop:
    cancelled: bool


class Bus:
    def __init__(self, stop_name):
        self.stop_name = stop_name
        self.ids = None

    async def get_next_buses(self):
        if self.ids == None:
            await self.get_ids()
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/stops/{self.ids}") as response:
                data = await response.json()
                stopTimes = list(data['results'])[:10]
                return stopTimes

    async def get_ids(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/stops?q={self.stop_name}") as response:
                data = await response.json()
                stop = list(data['results'])[0]
                self.ids = ",".join(stop['ids'])
