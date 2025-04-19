from kivymd.app import MDApp
from kivy.clock import Clock
from ui.layout import WeatherLayout
from datetime import datetime
from utils.location import GPSHelper  # Import your GPS helper

class WeatherApp(MDApp):
    
    def build(self):
        self.weather_ui = WeatherLayout()
        self.gps_helper = GPSHelper()  # Initialize GPSHelper
        Clock.schedule_once(lambda dt: self.get_location_and_weather(), 1)
        return self.weather_ui
    
    def get_location_and_weather(self):
        # Configure GPS and start fetching location
        self.gps_helper.configure(self.location_callback)
        
    def location_callback(self, lat, lon):
        # Location is updated here, use lat and lon to fetch weather
        default_city = self.get_city_from_coords(lat, lon)  # You can use a reverse geocoding API
        self.set_theme_by_time()
        self.weather_ui.update_weather(default_city)

    def get_city_from_coords(self, lat, lon):
        # Reverse geocoding could be used here to get city from lat/lon
        # For now, use a default value for testing
        return "Perambalur"  # Replace with actual reverse geocoding logic

    def set_live_wallpaper(self, condition_main, temperature):
        condition = condition_main.lower()
        current_hour = datetime.now().hour  
        is_daytime = 6 <= current_hour < 18

        video_path = "assets/backgrounds/sunny.mp4" if is_daytime else "assets/backgrounds/night.mp4"

        if "rain" in condition:
            video_path = "assets/backgrounds/rain2.mp4"
        elif "cloud" in condition and 15 <= temperature <= 25:
            video_path = "assets/backgrounds/cloud.mp4"
        elif "snow" in condition or temperature < 15:
            video_path = "assets/backgrounds/snow2.mp4"
        elif "thunder" in condition or "storm" in condition:
            video_path = "assets/backgrounds/cloud.mp4"

        self.weather_ui.video_bg.source = video_path
        self.weather_ui.video_bg.state = 'play'

    def apply_weather_theme(self, condition_main, temperature):
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

    def set_text_color(self, rgba):
        ui = self.weather_ui
        ui.location_label.text_color = rgba
        ui.temp_label.text_color = rgba
        ui.weather_label.text_color = rgba
        ui.weather_icon.text_color = rgba

    def set_theme_by_time(self):
        hour = datetime.now().hour
        self.theme_cls.theme_style = "Light" if 6 <= hour < 18 else "Dark"
        self.theme_cls.primary_palette = "Orange" if 6 <= hour < 18 else "Indigo"

if __name__ == '__main__':
    WeatherApp().run()
