import aiohttp
from .const import API_URL


class BusStop:
    cancelled: bool
    delay: int
    bus_number: str
    departure_time: str
    computed_time: str
    name: str
    seconds: int
    trip_name: str | None
    alerts: list[str]

    def __init__(self, cancelled, delay, bus_number, departure_time, computed_time, name, seconds, trip_name, alerts):
        self.cancelled = cancelled
        self.delay = delay
        self.bus_number = bus_number
        self.departure_time = departure_time
        self.computed_time = computed_time
        self.name = name
        self.seconds = seconds
        self.trip_name = trip_name
        self.alerts = alerts

    @classmethod
    def from_api_response(cls, data):
        
        return cls(
            cancelled=data['realtime']['cancelled'],
            delay=data['realtime']['delay'],
            bus_number=data['computed']['bus_number'],
            departure_time=data['departure_time'],
            computed_time=data['computed']['time'],
            name=data['computed']['name'],
            seconds=data['computed']['seconds'],
            trip_name=data['computed'].get('trip_name'),
            alerts = list(map(lambda x: x['header'], data['alerts']))
        )



class Bus:
    def __init__(self, stop_name, short_name_filter):
        self.stop_name = stop_name
        self.short_name_filter = short_name_filter

    async def fetch(self):
        result = {"alerts": [], "stops": []}
        async with aiohttp.ClientSession() as session:
            url = f"{API_URL}/stop/{self.stop_name.lower()}?"
            if self.short_name_filter:
                url += f"filternumbers={self.short_name_filter}"
            async with session.get(url) as response:
                data = await response.json()
                stopAlerts = list(data['result']['stop_alerts'])
                stopTimes = list(data['result']['stop_times'])[:10]
                result['alerts'] = [stopAlert['header'] for stopAlert in stopAlerts]
                result['stops'] = [BusStop.from_api_response(stop_time).__dict__ for stop_time in stopTimes]
                return result