import json

def save_weather_data(weather_data, filename="weather_data.json"):
    """Save weather data to a local JSON file."""
    with open(filename, 'w') as file:
        json.dump(weather_data, file)

def load_weather_data(filename="weather_data.json"):
    """Load weather data from a local JSON file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return None  # Return None if the file doesn't exist
