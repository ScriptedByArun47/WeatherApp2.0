from plyer import gps
from kivy.utils import platform

class GPSHelper:
    def __init__(self):
        self.latitude = None
        self.longitude = None
        self.on_location_callback = None

    def configure(self, callback):
        """Setup GPS with a callback function."""
        self.on_location_callback = callback
        if platform == 'android':
            gps.configure(on_location=self.on_location, on_status=self.on_status)
            gps.start(minTime=1000, minDistance=0)

    def on_location(self, **kwargs):
        self.latitude = kwargs['lat']
        self.longitude = kwargs['lon']
        if self.on_location_callback:
            self.on_location_callback(self.latitude, self.longitude)

    def on_status(self, stype, status):
        print(f"[GPS] Status: {stype} -> {status}")
