from kivymd.app import MDApp
from kivy.clock import Clock
import os
from ui.layout import WeatherLayout
from datetime import datetime
from kivy.resources import resource_find
from utils.location import GPSHelper

class WeatherApp(MDApp):
    
    def build(self):
        print("[INFO] App is starting...")  # Message during startup
        self.weather_ui = WeatherLayout()
        self.gps_helper = GPSHelper()
        Clock.schedule_once(lambda dt: self.get_location_and_weather(), 1)
        return self.weather_ui
    
    def get_location_and_weather(self):
        try:
            self.gps_helper.configure(self.location_callback)
        except Exception as e:
            print(f"[ERROR] Failed to configure GPS: {e}")
            # Fall back to default city if GPS fails
            self.location_callback(None, None)

    def location_callback(self, lat, lon):
        try:
            if lat is not None and lon is not None:
                default_city = self.get_city_from_coords(lat, lon)
            else:
                print("[WARN] Using default location due to GPS error.")
                default_city = "Perambalur"  # fallback city
            self.set_theme_by_time()
            self.weather_ui.update_weather(default_city)
        except Exception as e:
            print(f"[ERROR] Failed to update location/weather: {e}")

    def get_city_from_coords(self, lat, lon):
        try:
            # Reverse geocoding logic placeholder
            return "Perambalur"
        except Exception as e:
            print(f"[ERROR] Reverse geocoding failed: {e}")
            return "Perambalur"

    def set_live_wallpaper(self, condition_main, temperature):
        try:
            condition = condition_main.lower()
            current_hour = datetime.now().hour
            is_daytime = 6 <= current_hour < 18

            if "rain" in condition:
                video = "assets/backgrounds/rain2.mp4"
            elif "cloud" in condition and 15 <= temperature <= 25:
                video = "assets/backgrounds/cloud.mp4"
            elif "snow" in condition or temperature < 15:
                video = "assets/backgrounds/snow2.mp4"
            elif "thunder" in condition or "storm" in condition:
                video = "assets/backgrounds/cloud.mp4"
            else:
                video = "assets/backgrounds/sunny.mp4" if is_daytime else "assets/backgrounds/night.mp4"

            video_path = resource_find(video)

            if video_path and os.path.isfile(video_path):
                Clock.schedule_once(lambda dt: self._play_video(video_path), 1)
            else:
                print(f"[ERROR] Video path not found: {video_path}")
        except Exception as e:
            print(f"[ERROR] Failed to set live wallpaper: {e}")
    def _play_video(self, path):
        try:
            if hasattr(self.weather_ui, 'video_bg') and self.weather_ui.video_bg:
                self.weather_ui.video_bg.source = path
                self.weather_ui.video_bg.state = 'play'
        except Exception as e:
            print(f"[ERROR] Failed to play video: {e}")
            
    def apply_weather_theme(self, condition_main, temperature):
        try:
            condition = condition_main.lower()
            if "clear" in condition:
                self.theme_cls.primary_palette = "Amber"
                self.set_text_color((1, 0.9, 0.5, 1))
            elif "rain" in condition:
                self.theme_cls.primary_palette = "BlueGray"
                self.set_text_color((0.7, 0.85, 1, 1))
            elif "cloud" in condition:
                self.theme_cls.primary_palette = "Gray" if temperature >= 15 else "BlueGray"
                self.set_text_color((1, 1, 1, 1) if temperature >= 15 else (0.85, 0.85, 0.85, 1))
            elif "thunder" in condition or "storm" in condition:
                self.theme_cls.primary_palette = "DeepPurple"
                self.set_text_color((1, 1, 1, 1))
            elif "snow" in condition:
                self.theme_cls.primary_palette = "LightBlue"
                self.set_text_color((0.9, 0.95, 1, 1))
            elif "mist" in condition or "fog" in condition:
                self.theme_cls.primary_palette = "BlueGray"
                self.set_text_color((0.8, 0.8, 0.8, 1))
            else:
                self.theme_cls.primary_palette = "Teal"
                self.set_text_color((0.9, 1, 0.9, 1))
        except Exception as e:
            print(f"[ERROR] Failed to apply weather theme: {e}")

    def set_text_color(self, rgba):
        try:
            ui = self.weather_ui
            ui.location_label.text_color = rgba
            ui.temp_label.text_color = rgba
            ui.weather_label.text_color = rgba
            ui.weather_icon.text_color = rgba
        except Exception as e:
            print(f"[ERROR] Failed to set text color: {e}")

    def set_theme_by_time(self):
        try:
            hour = datetime.now().hour
            self.theme_cls.theme_style = "Light" if 6 <= hour < 18 else "Dark"
            self.theme_cls.primary_palette = "Orange" if 6 <= hour < 18 else "Indigo"
        except Exception as e:
            print(f"[ERROR] Failed to set theme by time: {e}")

if __name__ == '__main__':
    print("[INFO] App is running...")
    WeatherApp().run()
