from datetime import datetime  # To set date and time
import os



class Clock:
    def __init__(self, *args):
        self.respond = {}
        self.get_time()

    def get_time(self):
        now = datetime.now()
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


if __name__ == "__main__":
    print(Clock().respond)
