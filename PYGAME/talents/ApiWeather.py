from utilities import Helper
from get_project_root import root_path  # it is important to call root of project
from datetime import datetime as dt, timedelta

import sys
import json
import requests
from os.path import exists


# data example:
# {'feelsLike': 4, 'hour': 22, 'icon': '10n', 'temp': 5}


class WeatherApi:
    def __init__(self, *args):
        self.data = ""
        self.helper = Helper()
        self.PATH = root_path(ignore_cwd=False)
        # check file creation time and renew if it is older than 1 hour
        if not exists(self.PATH+"/assets/forecast.json"):
            self.get_weather()

        isOlder = self.helper.is_file_older_than(self.PATH+"/assets/forecast.json", timedelta(minutes=50))
        if isOlder:
            print("Weather data is old downloading...")
            self.get_weather()
        else:
            print("Weather data is new using it...")
        with open(self.PATH+"/assets/forecast.json", "r", encoding="utf-8"
                  ) as f:
            self.data = json.load(f)
        # current weather
        self.response = {
            "today_feels": f"{round(self.data['current']['feels_like'])}",
            "today_icon": f"{self.data['current']['weather'][0]['icon']}.png",
            "today_temp": f"{str(round(self.data['current']['temp']))}",
            "today_desc": f"{str(self.data['current']['weather'][0]['description'])}",
            "today_wind": f"{round(self.data['current']['wind_speed'])}",
            "day1_date": f"{self.helper.getDayName(self.data['daily'][1]['dt'])}",
            "day1_temp": f"{round(self.data['daily'][1]['temp']['day'])}",
            "day1_icon": f"{self.data['daily'][1]['weather'][0]['icon']}.png",
            "day1_desc": f"{self.data['daily'][1]['weather'][0]['description']}",
            "day2_date": f"{self.helper.getDayName(self.data['daily'][2]['dt'])}",
            "day2_temp": f"{round(self.data['daily'][2]['temp']['day'])}",
            "day2_icon": f"{self.data['daily'][2]['weather'][0]['icon']}.png",
            "day2_desc": f"{self.data['daily'][2]['weather'][0]['description']}",
            "day3_date": f"{self.helper.getDayName(self.data['daily'][3]['dt'])}",
            "day3_temp": f"{round(self.data['daily'][3]['temp']['day'])}",
            "day3_icon": f"{self.data['daily'][3]['weather'][0]['icon']}.png",
            "day3_desc": f"{self.data['daily'][3]['weather'][0]['description']}",
            "day4_date": f"{self.helper.getDayName(self.data['daily'][4]['dt'])}",
            "day4_temp": f"{round(self.data['daily'][4]['temp']['day'])}",
            "day4_icon": f"{self.data['daily'][4]['weather'][0]['icon']}.png",
            "day4_desc": f"{self.data['daily'][4]['weather'][0]['description']}",
        }

    def get_weather(self):
        city = self.helper.getCity()
        weather = None

        try:
            url = "https://api.openweathermap.org/data/2.5/onecall?lat=36.7741&lon=30.7178&appid=7a7da2092e3a7fc1b6e0970d76b7743b&units=metric&lang=tr"
            # url = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid=7a7da2092e3a7fc1b6e0970d76b7743b&units=metric&lang=tr'.format(city)
            res = requests.get(url)
            # res = res.json()
            json_file = self.PATH+"/assets/forecast.json"
            with open(json_file, "wb") as fd:
                fd.write(res.content)
            return True
        except:
            return False


if __name__ == "__main__":
    x = Weather()
    print(Weather().response)
