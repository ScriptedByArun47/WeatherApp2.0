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
        try:
            if platform == 'android':
                gps.configure(on_location=self.on_location, on_status=self.on_status)
                gps.start(minTime=1000, minDistance=0)
                print("[INFO] GPS started successfully.")
            else:
                print("[WARN] GPS is not supported on this platform.")
        except NotImplementedError:
            print("[ERROR] GPS is not implemented on this platform.")
        except Exception as e:
            print(f"[ERROR] Failed to configure/start GPS: {e}")

    def on_location(self, **kwargs):
        try:
            self.latitude = kwargs.get('lat')
            self.longitude = kwargs.get('lon')

            if self.latitude is None or self.longitude is None:
                print("[WARN] Received location update with missing data.")
                return

            print(f"[INFO] Location update received: lat={self.latitude}, lon={self.longitude}")

            if self.on_location_callback:
                self.on_location_callback(self.latitude, self.longitude)
            else:
                print("[WARN] No location callback set.")
        except Exception as e:
            print(f"[ERROR] Failed to process location update: {e}")

    def on_status(self, stype, status):
        try:
            print(f"[GPS] Status: {stype} -> {status}")
        except Exception as e:
            print(f"[ERROR] Failed to handle GPS status: {e}")
