from datetime import datetime
import requests
import json
import os


class WeatherService:
    def __init__(self, cache_dir):
        self.cache_dir = cache_dir
        self.session = requests.Session()
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def __get_cache_filename__(self, long, lat):
        return os.path.join(self.cache_dir, f"{long}_{lat}.json")

    def get_weather(self, long, lat, time):
        year, month, day, hour = time.year, time.month, time.day, time.hour
        # Round lat and long to 0.1 degrees
        long = round(long, 2)
        lat = round(lat, 2)
        print(f'Getting weather for {long}, {lat} at {time}')
        cache_filename = self.__get_cache_filename__(long, lat)
        if os.path.exists(cache_filename):
            with open(cache_filename, 'r') as f:
                cached_weather = json.load(f)

        else:
            # Request the hourly historical weather from open-meteo
            response = self.session.get(f'https://archive-api.open-meteo.com/v1/archive',
                                        params={'latitude': lat, 'longitude': long, 'hourly': 'cloudcover', 'start_date': '2021-07-01', 'end_date': '2021-07-20'})
            assert response.status_code == 200, f'Error getting weather: {response.text}'
            cached_weather = response.json()
            assert 'hourly' in cached_weather, f'No weather data found: {cached_weather}'
            cached_weather = cached_weather['hourly']
            with open(cache_filename, 'w') as f:
                json.dump(cached_weather, f)
        # Find the weather for the specified time
        for time_hour, cloud_cover in zip(cached_weather['time'], cached_weather['cloudcover']):
            time_hour = datetime.strptime(time_hour, '%Y-%m-%dT%H:%M')
            if time_hour.year == year and time_hour.month == month and time_hour.day == day and time_hour.hour == hour:
                return 1-int(cloud_cover)/100
        return 1  # If no weather is found, assume it is clear
