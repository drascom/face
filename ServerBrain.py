# import json
import random

# local imports
# from engine.config import ROOT_DIR
from nlp import run as predict
from talents.Wikipedia2 import AskWiki
from talents.Weather import Weather
from talents.Clock import Clock
from talents.Alarm import RecordAlarm


# from engine import predictions
# from engine.predictions import get_response


#################################
# data = {
#     "face":"wakeup",
#     "data":{},
#     "screen":"home",
#     "sleep" : 8
#     "sfx":"",
#     "text_for_sound":"test",
#     "text_for_console":"test"
#     }


class Brain:
    def __init__(self):
        # incoming command from robot
        self.command = {}
        # incoming data from robot
        self.fromRobot = {}
        # answer from prediction
        self.fromPrediction = {}
        # incoming data from talents
        self.fromTalent = {}
        # returning data sample
        self.toRobot = {}

    def run(self,request):
        self.command = request["command"]
        self.fromRobot = request["data"]
        print("[BRAIN] Gelen Komut", self.command)
        self.fromPrediction = predict(self.command)
        print("[BRAIN] Tag:", self.fromPrediction["tag"])
        if "action" in self.fromPrediction:
            print("Action: ", self.fromPrediction["action"])
        if self.fromPrediction is not False:
            if "next" in self.fromPrediction:
                self.toRobot["next"] = self.fromPrediction["next"]
            if "responses" in self.fromPrediction:
                self.toRobot["text_for_sound"] = random.choice(
                    self.fromPrediction["responses"])
            if self.fromPrediction["type"] == "function":
                try:
                    method_to_call = getattr(
                        self, self.fromPrediction["action"])
                    method_to_call()
                except:
                    self.toRobot["text_for_sound"] = "böyle bir fonksiyon yok"
                    self.toRobot["text_for_console"] = self.fromPrediction["action"] + \
                        " böyle bir fonksiyon yok"
                    pass
        print("[BRAIN] Robota Giden: ", self.toRobot)
        return self.toRobot

    ######## Clock functions#########################
    def runClock(self):
        try:
            clock = Clock().respond
            alarm = RecordAlarm().respond
            self.toRobot["screen"] = "time_screen"
            self.toRobot["data"] = alarm
            self.toRobot["sleep"] = 8
            self.toRobot[
                "text_for_sound"
            ] = f"Şu an saat {clock['day']} {clock['hour']} {clock['min']} "
        except:
            print("saat okunamadı")

    # WEATHER FUNCTIONS ###############################33
    def runWeather(self):
        try:
            fromTalent = Weather().response
            self.toRobot["screen"] = "weather_screen"
            self.toRobot["data"] = fromTalent
            self.toRobot["sleep"] = 8
            self.toRobot[
                "text_for_sound"
            ] = f"Şu an hava {fromTalent['today_desc']}, {fromTalent['today_temp']} , rüzgar hızı  saatte {fromTalent['today_wind']} kilometre"
        except:
            print("hava okunamadı")

    # ALARM FUNCTİONS ##################################333
    def showAlarm(self):
        try:
            fromTalent = RecordAlarm().respond
            if fromTalent["status"] == "on":
                text_for_sound = (
                    f"Alarm {fromTalent['hour']} {fromTalent['min']} için açık"
                )
            else:
                text_for_sound = f"Alarm kapalı."
            self.toRobot["screen"] = "alarm_screen"
            self.toRobot["data"] = fromTalent
            self.toRobot["sleep"] = 8
            self.toRobot["text_for_sound"] = text_for_sound
        except:
            print("[BRAIN] Alarm okunamadı")

    def changeAlarm(self):
        self.toRobot["screen"] = "alarm_screen"

    def _get_hour(self):
        fromTalent = False
        try:
            fromTalent = RecordAlarm().setHour(self.fromRobot)
        except:
            self.toRobot["text_for_console"] = "[BRAIN] Saat yazılamadı"
        if fromTalent is False:
            self.toRobot["text_for_sound"] = fromTalent["error"]
            self.toRobot["text_for_console"] = "[BRAIN] Metin rakam olarak gelmedi"

    def _get_min(self):
        try:
            fromTalent = RecordAlarm().setMinute(self.fromRobot)
            self.toRobot["text_for_console"] = "[BRAIN] Dakika YAZILDI"
        except:
            self.toRobot["text_for_console"] = "[BRAIN] Dakika yazılamadı"

    def set_alarm(self):
        decision = predict(self.fromRobot)
        print("[BRAIN] set alarm tahmini", decision["tag"])
        if "confirm" in decision:
            try:
                fromTalent = RecordAlarm().enableAlarm()
                self.toRobot["text_for_sound"] = "tamam, alarm pasif"
            except:
                self.toRobot["text_for_console"] = "[BRAIN] Alarm aktif edilemedi"
        else:
            try:
                fromTalent = RecordAlarm().enableAlarm()
                self.toRobot["text_for_sound"] = "tamam, alarm aktif"
            except:
                self.toRobot["text_for_console"] = "[BRAIN] Alarm aktif edilemedi"

    def enableAlarm(self):
        try:
            fromTalent = RecordAlarm().enableAlarm()
            self.toRobot["text_for_sound"] = "tamam, alarm aktif"
        except:
            self.toRobot["text_for_console"] = "Alarm Kurulamadı"

    def disableAlarm(self):
        try:
            fromTalent = RecordAlarm().disableAlarm()
            self.toRobot["text_for_sound"] = "tamam, alarm pasif"
        except:
            self.toRobot["text_for_console"] = "Alarm Kurulamadı"

    ##############   wikipedia #####################
    def askWiki(self):
        self.toRobot["face"] = "listening"

    def _setup_wiki(self):
        self.toRobot["face"] = "searching"
        self.toRobot["data"] = self.fromRobot

    def _search_wiki(self):
        fromTalent = AskWiki(self.fromRobot).response
        if "error" not in fromTalent:
            self.toRobot["face"] = "found"
            self.toRobot["text_for_sound"] = "buldum," + fromTalent
            self.toRobot["sleep"] = 8
        else:
            self.toRobot["text_for_sound"] = fromTalent["error"]

if __name__ == "__main__":
    request = {"command":"saat","data":""}
    brain = Brain()
    respond = brain.run(request)
    print(respond)