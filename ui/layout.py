from kivymd.uix.boxlayout import MDBoxLayout, BoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRectangleFlatButton, MDIconButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivy.uix.video import Video
from kivy.uix.floatlayout import FloatLayout
from kivy.metrics import dp
from kivy.resources import resource_find
import socket
from threading import Timer
from kivy.clock import Clock
import requests, os, pygame
from utils.suggestions import get_suggestions, smart_weather_notification
from utils.weather_data import save_weather_data, load_weather_data 
from datetime import datetime

from components.sun_tracker import SunTrackerBar
from kivymd.app import MDApp


API_KEY = "9004b2a6daa4818401f901ee65eae86a"


class WeatherLayout(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_city = None
        self.weather_data = None

        video_file = resource_find("assets/backgrounds/sunny.mp4") or ""
        if not video_file:
            print("[ERROR] Default video not found!")
        else:
            print(f"[INFO] Loaded video: {video_file}")

        self.video_bg = Video(
            source=video_file,
            state='play',
            options={'eos': 'loop'},
            volume=0,
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0}
        )
        self.add_widget(self.video_bg)
        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"[ERROR] pygame mixer init failed: {e}")

        self.current_music = None

        self.scroll_view = MDScrollView(
            size_hint=(0.5, 0.85),
            
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )

        self.foreground = MDBoxLayout(
            orientation="vertical",
            padding=20,
            spacing=40,
            size_hint_y=None
        )
        self.foreground.bind(minimum_height=self.foreground.setter("height"))

        self.city_input = MDTextField(
    hint_text="Enter city name...",
    mode="rectangle",
    size_hint=(1, None),
    height=dp(48),  # Ideal for text fields (accessible size)
    font_size="16sp",
    pos_hint={"center_x": 0.5}
     )

        self.search_button = MDRectangleFlatButton(
    text="Search Weather",
    size_hint=(1, None),
    height=dp(44),  # Minimum for comfortable clicking
    font_size="16sp",
    pos_hint={"center_x": 0.5},
    on_release=self.search_city_weather,
    icon="magnify"
        )
        self.weather_icon = MDIconButton(
            icon="weather-cloudy",
            icon_size="64sp",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            pos_hint={"center_x": 0.5}
        )
        self.location_label = MDLabel(
            text="Fetching location...",
            halign="center",
            font_style="Subtitle1",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)
        )
       
        
        self.temp_label = MDLabel(
            text="",
            halign="center",
            font_style="H5",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            bold=True
        )
        self.weather_label = MDLabel(
            text="",
            halign="center",
            font_style="Subtitle1",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)
        )

        self.sun_tracker = SunTrackerBar()

        for widget in [
            self.city_input, self.search_button, self.weather_icon,
            self.location_label, self.temp_label, self.weather_label,
            
            self.sun_tracker
        ]:
            self.foreground.add_widget(widget)

        self.scroll_view.add_widget(self.foreground)
        self.add_widget(self.scroll_view)

    
        

    def play_music_for_weather(self, condition, temp):
        condition = condition.lower()
        is_daytime = 6 <= datetime.now().hour < 18

        # Default music selection based on time
        music_file = "assets/music/summer.mp3" if is_daytime else "assets/music/night.mp3"

        # Weather-based override
        if "rain" in condition:
            music_file = "assets/music/rain.mp3"
        elif "cloud" in condition and 15 <= temp <= 25:
            music_file = "assets/music/cloud.mp3"
        elif "snow" in condition or temp < 15:
            music_file = "assets/music/snow.mp3"

        # Resolve full path using resource_find
        resolved_path = resource_find(music_file)

        if not resolved_path:
            print(f"[ERROR] Music file not found: {music_file}")
            return

        try:
            if resolved_path != self.current_music:
                if pygame.mixer.get_init() is None:
                    pygame.mixer.init()
                pygame.mixer.music.stop()
                pygame.mixer.music.load(resolved_path)
                pygame.mixer.music.play(-1)
                self.current_music = resolved_path
                print(f"[INFO] Playing: {music_file}")
        except Exception as e:
            print(f"[ERROR] Music playback failed: {e}")

    def get_weather_icon(self, condition):
        condition = condition.lower()
        if "clear" in condition:
            return "weather-sunny"
        elif "rain" in condition:
            return "weather-rainy"
        elif "cloud" in condition:
            return "weather-cloudy"
        elif "snow" in condition:
            return "weather-snowy"
        elif "thunder" in condition or "storm" in condition:
            return "weather-lightning"
        return "weather-partly-cloudy"

    def search_city_weather(self, instance):
        city = self.city_input.text.strip()
        if city:
            self.update_weather(city)


    def start_background_weather_updates(self, interval_seconds=1800):
        def update_loop():
            self.update_weather(self.last_city)
            Timer(interval_seconds, update_loop).start()
    
        update_loop()

    def add_forecast_list(self, forecast_data):
        if hasattr(self, "forecast_widgets"):
            for widget in self.forecast_widgets:
                self.foreground.remove_widget(widget)

        self.forecast_widgets = []
        for date, desc, temp_min, temp_max in forecast_data:
            card = MDCard(
            size_hint=(1, None),
            height=dp(80),
            padding=dp(10),
            radius=[dp(12)],
            md_bg_color=(1, 1, 1, 0.2),
            elevation=2
        )
            layout = MDBoxLayout(orientation="horizontal", spacing=10)
            layout.add_widget(MDIconButton(icon=self.get_weather_icon(desc), theme_text_color="Custom", text_color=(1, 1, 1, 1)))
            layout.add_widget(MDLabel(text=date, size_hint_x=0.3,theme_text_color="Custom", text_color=(1, 1, 1, 1)))
            layout.add_widget(MDLabel(text=desc, size_hint_x=0.3,theme_text_color="Custom", text_color=(1, 1, 1, 1)))
            layout.add_widget(MDLabel(text=f"{temp_min:.1f}° / {temp_max:.1f}°", halign="right", size_hint_x=0.4,theme_text_color="Custom", text_color=(1, 1, 1, 1)))

            card.add_widget(layout)
            self.foreground.add_widget(card)
            self.forecast_widgets.append(card)

    def update_weather(self, city):
        self.last_city = city
        """Update weather intelligently based on internet availability."""

        if  WeatherLayout.is_connected():
            print("🌐 Online mode")
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"

            try:
                response = requests.get(url)
                forecast_response = requests.get(forecast_url)

                if response.status_code == 200 and forecast_response.status_code == 200:
                    data = response.json()
                    forecast_data = forecast_response.json()

                    temp = data['main']['temp']
                    desc = data['weather'][0]['description']
                    condition_main = data['weather'][0]['main']
                    country = data['sys']['country']
                    wind_speed = data['wind']['speed']
                    uv_index = 5  # Optional

                    sunrise_ts = data["sys"]["sunrise"]
                    sunset_ts = data["sys"]["sunset"]
                    current_ts = data["dt"]
                    self.sun_tracker.sunrise_label.text = datetime.fromtimestamp(sunrise_ts).strftime("%I:%M %p")
                    self.sun_tracker.sunset_label.text = datetime.fromtimestamp(sunset_ts).strftime("%I:%M %p")
                    Clock.schedule_once(lambda dt: self.sun_tracker.update_sun_position(
                        sunrise_ts, sunset_ts, current_ts), 1)

                    daily_forecast = []
                    for entry in forecast_data['list']:
                        if "12:00:00" in entry['dt_txt']:
                            date_obj = datetime.strptime(entry['dt_txt'], "%Y-%m-%d %H:%M:%S")
                            formatted_date = date_obj.strftime("%a, %d %b")
                            temp_min = entry['main']['temp_min']
                            temp_max = entry['main']['temp_max']
                            weather_desc = entry['weather'][0]['main']
                            daily_forecast.append((formatted_date, weather_desc, temp_min, temp_max))
                        if len(daily_forecast) == 4:
                            break

                    weather_data = {
                        'temp': temp,
                        'condition': desc,
                        'wind_speed': wind_speed,
                        'uv_index': uv_index,
                        'country': country,
                        'forecast': daily_forecast
                    }
                    save_weather_data(weather_data)

                    self.display_weather(weather_data)
                    self.add_forecast_list(daily_forecast)
                    smart_weather_notification(weather_data)

                    self.play_music_for_weather(condition_main, temp)
                    MDApp.get_running_app().apply_weather_theme(condition_main, temp)
                    MDApp.get_running_app().set_live_wallpaper(condition_main, temp)

                else:
                    self.temp_label.text = "City not found."

            except Exception as e:
                self.temp_label.text = f"Error: {str(e)}"

        else:
            print("📴 Offline mode")
            weather_data = load_weather_data()
            if weather_data:
                self.display_weather(weather_data)
                self.add_forecast_list(weather_data.get("forecast", []))
            else:
                self.temp_label.text = "No internet & no cached data available."
    def is_connected():
        try:
            # Try to resolve a host, simple way to check internet
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            return True
        except OSError:
            return False
    
    def display_weather(self, weather_data):
        temp = weather_data.get('temp', 20)
        desc = weather_data.get('condition', 'Clear')
        condition_main = weather_data.get('condition', 'Clear')
        wind_speed = weather_data.get('wind_speed', 0)
        country = weather_data.get('country', 'N/A')

        self.location_label.text = f"Location: {self.last_city.title()}, {country}"
        self.temp_label.text = f"Temperature: {temp:.2f}°C"
        self.weather_label.text = f"Weather: {desc.capitalize()}"
        self.weather_icon.icon = self.get_weather_icon(condition_main)

        smart_weather_notification(weather_data)
