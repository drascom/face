import pygame
import psutil
import sys
from time import sleep
import threading
import socket
import os
import json
import ipinfo
from get_project_root import root_path  # it is important to call root of project
import speech_recognition as sr
from gtts import gTTS
from datetime import datetime as dt


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


# now, to clear the screen
cls()
pygame.font.init()


class SensorData:
    def __init__(self):
        self.data = {}
        self.data['CPU_TEMP'] = 0
        self.data['BATTERY_PERCENTAGE'] = 0
        self.data['BATTERY_LEFT'] = 0
        self.data['PLUGGEDIN'] = False
        self.server_thread = threading.Thread(
            target=self.read_data, daemon=True)
        self.server_thread.start()

    def read_data(self):
        while True:
            # ==============  Battery ================
            if self.data['BATTERY_PERCENTAGE'] == 0:
                print("Battery check started")
            battery = psutil.sensors_battery()

            def convertTime(seconds):
                minutes, seconds = divmod(seconds, 60)
                hours, minutes = divmod(minutes, 60)
                return "%d:%02d:%02d" % (hours, minutes, seconds)

            self.data['BATTERY_PERCENTAGE'] = round(battery.percent, 1)
            self.data['BATTERY_LEFT'] = convertTime(battery.secsleft)
            self.data['PLUGGEDIN'] = battery.power_plugged

            # =============== CPU TEMP ===================
            if sys.platform == "linux" or sys.platform == "linux2":
                path = '/sys/class/thermal/thermal_zone0/temp'
                if self.data['CPU_TEMP'] == 0:
                    print("Temp check started")
                with open(os.path.join(os.path.dirname(__file__), path), 'r') as input_file:
                    temp = float(input_file.read())
                    tempB = temp/1000
                    if self.data['CPU_TEMP'] != tempB:
                        self.data['CPU_TEMP'] = tempB
            sleep(1)


class Connection:
    def __init__(self):
        self.stream_lock = threading.Lock()
        self.hostname = socket.gethostname()
        self.IP = socket.gethostbyname(self.hostname)
        self.PORT = 5005
        self.messageSent = {'current': '', 'mode': ''}
        self.messageReceived = {}
        self.current = ""
        self.isConnected = False
        self.server_thread = threading.Thread(target=self.host_game, daemon=True, args=(
            self.IP, self.PORT))
        self.server_thread.start()

    def process_command(self):
        self.messageReceived.pop('ping', None)

    def host_game(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen()
        print("Server is ready")
        try:
            while True:
                client, addr = self.server.accept()
                self.isConnected = True
                self.client_thread = threading.Thread(
                    target=self.listener, daemon=True, args=(client, addr))
                self.client_thread.start()
                print("connected")
        except:
            self.isConnected = False
            print("cant connect")

    def listener(self, client, address):
        print("Client Connected ! ", address)
        while True:
            try:
                data = client.recv(2048)
                if not data:  # if clients disconnected
                    break
                self.messageReceived = json.loads(data.decode('utf-8'))
            except:  # if clients shutdown abnormally
                print("Transmission Lost !")
                break
            # print("received: ", self.received_data, self.messageSent)
            client.sendall(json.dumps(self.messageSent).encode('utf-8'))
        print("Client Disconnected")
        client.close()


class Services:
    def __init__(self):
        self.Sensors = SensorData()
        self.Server = Connection()
        self.audio = Audio()
        self.old_scene_name = ""

    def name_constructor(self):

        if "command" in self.Server.messageReceived and self.Server.messageReceived['command'] != "":
            msg = self.Server.messageReceived['command']
            # print("gelen ", msg)
            if self.old_scene_name != msg:
                self.old_scene_name = msg
                return 'Scene' + self.Server.messageReceived['command'].capitalize()
        else:
            return False

    def page_selector(self, current):
        # set outgoing message with new scene name
        self.Server.messageSent['current'] = current.name
        self.Server.messageSent.update(self.Sensors.data)
        # set new active scene if command exist at incoming data
        if self.Server.isConnected and self.Server.messageReceived:
            return self.name_constructor()


class Helper:
    def __init__(self):
        self.PATH = root_path(ignore_cwd=False)
        self.clock_timer = None
        self.clock_blink = ':'
        with open(self.PATH+'/assets/config.json') as f:
            self.config = json.load(f)

    def get_font(self, type: str, size: int):
        if type == 'digi':
            return pygame.font.Font(self.PATH+"/assets/fonts/digital-7-mono.ttf", int(640 * size/100))
        elif type == 'lux':
            return pygame.font.Font(self.PATH+"/assets/fonts/DejaVuSansMono.ttf", int(640 * size/100))
        else:
            return pygame.font.Font(self.PATH+"/assets/fonts/DroidSans.ttf", int(640 * size/100))

    def get_time_sentence(self):
        now = dt.now()
        if os.name == 'nt':
            hour24 = now.strftime("%#H")
            hour12 = now.strftime("%#I")
        else:
            hour24 = now.strftime("%-H")
            hour12 = now.strftime("%-I")
        current_min = now.strftime("%M")
        hour = int(hour24)
        if hour >= 0 and hour <= 5:
            zaman = "gece"
        elif hour >= 6 and hour <= 12:
            zaman = "gündüz"
        elif hour >= 13 and hour <= 18:
            zaman = "öğleden sonra"
        elif hour >= 19 and hour <= 24:
            zaman = "akşam"
        else:
            zaman = "hımm"
        self.respond = {"day": zaman, "hour": hour12, "min": current_min}

    def get_current_time(self):
        if self.clock_timer != dt.now().strftime('%S'):
            if int(dt.now().strftime('%f')) > 99999:
                self.clock_timer = dt.now().strftime('%S')
            self.blink = ':'
        elif self.clock_timer == dt.now().strftime('%S'):
            self.blink = ' '
        hour = dt.now().strftime("%I")
        return f"{hour}{self.blink}{dt.now().strftime('%M')}"

    def get_current_seconds(self):
        hour = dt.now().strftime("%H")
        return f"{self.blink}{dt.now().strftime('%S')}"

    def get_current_alarm(self):
        # return alarms['daily']
        return {'alarm': self.config['alarm'], 'status': self.config['alarm_status']}

    def get_current_date(self) -> str:
        return dt.today().strftime("%B %d, %Y")

    def is_file_older_than(self, file, delta):
        cutoff = dt.utcnow() - delta
        mtime = dt.utcfromtimestamp(os.path.getmtime(file))
        if mtime < cutoff:
            return True
        return False

    # compare 2 times older than delta
    def is_time_older_than(self, time, delta):
        print(dt.utcnow() - time, delta)
        if (dt.utcnow() - time) > delta:
            return True
        return False

    # get city name from ipinfo.io
    def getCity(self):
        access_token = '16cb61bf42b6e4'
        handler = ipinfo.getHandler(access_token)
        details = handler.getDetails()
        return details.city

    def convert_hour(self, hour):
        if hour > 12:
            return f"{hour - 12} pm"
        if hour == 0:
            return "12 am"

    def getDayName(self, value):
        days = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cts", "Pzr"]
        dt_object = dt.fromtimestamp(value)
        return days[dt_object.weekday()]


class Audio:
    def __init__(self):
        # for mic in sr.Microphone.list_microphone_names():
        #     print(mic)
        self.r = sr.Recognizer()
        self.m = sr.Microphone()
        # self.server_thread = threading.Thread(target=self.listen_google)
        # self.server_thread.start()
        print("Sound Server ready...")

    def speak(audioString):
        # print(audioString)
        tts = gTTS(text=audioString, lang='tr')
        tts.save("audio.mp3")
        audio = pygame.mixer.Sound("audio.mp3")
        audio.play()
        # os.system("mpg321 audio.mp3")

    def listen_google(self):
        query = False
        with self.m as source:
            print("Waiting...")
            self.r.adjust_for_ambient_noise(source)
            self.r.dynamic_energy_threshold = 3000
            audio = self.r.listen(source)
        try:
            print("Recognizing...")
            query = self.r.recognize_google(audio, language='tr-TR')
            if query is not None:
                return query.lower()
        except sr.WaitTimeoutError:
            pass
        except sr.UnknownValueError:
            print("anlamadım")
            pass
        except sr.RequestError:
            print("Network error.")
            pass
        return query


if __name__ == '__main__':
    while True:
        pass
