from plyer import notification
from threading import Timer
import time
import random  # Replace with actual API in real usage

# Store previous weather for comparison
previous_weather = {}

def get_suggestions(weather_data):
    suggestions = []

    temp = weather_data.get('temp', 20)
    condition = weather_data.get('condition', '').lower()
    wind_speed = weather_data.get('wind_speed', 0)
    uv_index = weather_data.get('uv_index', 0)

    if "rain" in condition or "drizzle" in condition:
        suggestions.append("🌧️ Rain Alert: Carry an umbrella and wear waterproof shoes ☔🧥")

    if "snow" in condition:
        suggestions.append("❄️ Snow Alert: Dress in thermal layers, gloves, and insulated boots 🧤🥾")

    if "fog" in condition:
        suggestions.append("🌫️ Fog Alert: Visibility is low—wear bright or reflective clothing 🦺")

    if temp > 35:
        suggestions.append("🔥 Heat Alert: Avoid peak sun hours and wear breathable fabrics 🧊👕")
    elif temp > 30:
        suggestions.append("☀️ Hot Weather: Stay hydrated, wear light colors and a hat 🧢")

    elif temp < 5:
        suggestions.append("🥶 Cold Alert: Wear thermal layers, scarf, and gloves 🧣🧤")
    elif temp < 10:
        suggestions.append("🧥 Cool Weather: A warm jacket is recommended")

    if uv_index > 7:
        suggestions.append("🌞 UV Alert: Use SPF 30+ sunscreen, sunglasses, and a cap 😎🧴")
    elif 5 <= uv_index <= 7:
        suggestions.append("☀️ Moderate UV: Consider sunglasses and sunscreen 😌")

    if wind_speed > 30:
        suggestions.append("🌪️ Strong Winds: Wear a windbreaker and secure loose clothes 🧥")
    elif wind_speed > 20:
        suggestions.append("💨 Breezy: Might want to bring a light jacket")

    if "clear" in condition and 18 <= temp <= 25:
        suggestions.append("🌤️ Perfect Weather: T-shirt and jeans kind of day 👕👖")

    return suggestions


def weather_has_changed(current, previous):
    if not previous:
        return True

    temp_diff = abs(current.get("temp", 0) - previous.get("temp", 0))
    wind_diff = abs(current.get("wind_speed", 0) - previous.get("wind_speed", 0))
    uv_diff = abs(current.get("uv_index", 0) - previous.get("uv_index", 0))
    condition_changed = current.get("condition", "").lower() != previous.get("condition", "").lower()

    return temp_diff > 3 or wind_diff > 5 or uv_diff > 2 or condition_changed


def send_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=10
    )


def smart_weather_notification(current_weather,delay=10):
    global previous_weather

    if weather_has_changed(current_weather, previous_weather):
        suggestions = get_suggestions(current_weather)
        delay = 0
        for suggestion in suggestions:
            Timer(delay, lambda s=suggestion: send_notification("Smart Clothing Tip 👕", s)).start()
            delay += 5
        previous_weather = current_weather.copy()


# ❗ Simulate weather update (replace this with your real app's weather API)
def fetch_weather_mock():
    return {
        "temp": random.randint(0, 38),
        "condition": random.choice(["clear", "rain", "fog", "snow", "drizzle"]),
        "wind_speed": random.randint(0, 40),
        "uv_index": random.randint(0, 10)
    }


# 🔁 Periodic weather check (every 30 minutes = 1800 seconds)
def start_periodic_weather_check(interval_seconds=1800):
    def check_and_reschedule():
        current_weather = fetch_weather_mock()  # Replace with real API call
        print(f"🔄 Checking weather: {current_weather}")
        smart_weather_notification(current_weather)
        Timer(interval_seconds, check_and_reschedule).start()

    check_and_reschedule()


# 👉 Manual trigger for your app:
def trigger_from_app(new_weather_data):
    smart_weather_notification(new_weather_data)


# Uncomment this line to start automatic 30-minute checks
# start_periodic_weather_check()

# OR trigger manually like this:
# trigger_from_app({
#     "temp": 9,
#     "condition": "rain",
#     "wind_speed": 25,
#     "uv_index": 3
# })     every seconds notification