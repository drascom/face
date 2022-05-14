from robot.core.utils import getCity, convertTimestamp, getDayName, is_file_older_than
from datetime import datetime as dt, timedelta
from config.definitions import ROOT_DIR
import os
import sys
import requests
import json


def get_weather():
    city = getCity()
    weather = None

    try:
        url = "https://api.openweathermap.org/data/2.5/onecall?lat=36.7741&lon=30.7178&appid=7a7da2092e3a7fc1b6e0970d76b7743b&units=metric&lang=tr"
        # url = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid=7a7da2092e3a7fc1b6e0970d76b7743b&units=metric&lang=tr'.format(city)
        res = requests.get(url)
        # res = res.json()
        json_file = os.path.join(ROOT_DIR, "assets", "forecast.json")
        with open(json_file, "wb") as fd:
            fd.write(res.content)
        return True
    except:
        return False


def convert_hour(hour):
    if hour > 12:
        return f"{hour - 12} pm"

    if hour == 0:
        return "12 am"

    return f"{hour} am"


# data example:
# {'feelsLike': 4, 'hour': 22, 'icon': '10n', 'temp': 5}
class Weather:
    def __init__(self, *args):
        self.data = ""
        # check file creation time and renew if it is older than 1 hour
        isOlder = is_file_older_than(
            os.path.join(ROOT_DIR, "assets",
                         "forecast.json"), timedelta(minutes=50)
        )
        if isOlder:
            print("Weather data is old downloading...")
            get_weather()
        else:
            print("Weather data is new using it...")
        with open(
            os.path.join(ROOT_DIR, "assets", "forecast.json"), "r", encoding="utf-8"
        ) as f:
            self.data = json.load(f)
            # current weather
        self.response = {
            "today_feels": f"{round(self.data['current']['feels_like'])}",
            "today_icon": f"{self.data['current']['weather'][0]['icon']}.png",
            "today_temp": f"{str(round(self.data['current']['temp']))}°",
            "today_desc": f"{str(self.data['current']['weather'][0]['description'])}",
            "today_wind": f"{round(self.data['current']['wind_speed'])}",
            "day1_date": f"{getDayName(self.data['daily'][1]['dt'])}",
            "day1_temp": f"{round(self.data['daily'][1]['temp']['day'])}°",
            "day1_icon": f"{self.data['daily'][1]['weather'][0]['icon']}.png",
            "day1_desc": f"{self.data['daily'][1]['weather'][0]['description']}",
            "day2_date": f"{getDayName(self.data['daily'][2]['dt'])}",
            "day2_temp": f"{round(self.data['daily'][2]['temp']['day'])}°",
            "day2_icon": f"{self.data['daily'][2]['weather'][0]['icon']}.png",
            "day2_desc": f"{self.data['daily'][2]['weather'][0]['description']}",
            "day3_date": f"{getDayName(self.data['daily'][3]['dt'])}",
            "day3_temp": f"{round(self.data['daily'][3]['temp']['day'])}°",
            "day3_icon": f"{self.data['daily'][3]['weather'][0]['icon']}.png",
            "day3_desc": f"{self.data['daily'][3]['weather'][0]['description']}",
            "day4_date": f"{getDayName(self.data['daily'][4]['dt'])}",
            "day4_temp": f"{round(self.data['daily'][4]['temp']['day'])}°",
            "day4_icon": f"{self.data['daily'][4]['weather'][0]['icon']}.png",
            "day4_desc": f"{self.data['daily'][4]['weather'][0]['description']}",
        }


if __name__ == "__main__":
    get_weather()
    print(Weather().response)
