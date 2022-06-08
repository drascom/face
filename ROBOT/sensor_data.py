import os
from pickle import TRUE
import psutil
from database import DataRecords


DB = DataRecords()
CPU_TEMP=0
BATTERY_PERCENTAGE = 0
BATTERY_LEFT = 0
def checkBattery():
    global BATTERY
    battery = psutil.sensors_battery()
    def convertTime(seconds):
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return "%d:%02d:%02d" % (hours, minutes, seconds)
    
    BATTERY_PERCENTAGE =battery.percent
    BATTERY_LEFT = convertTime(battery.secsleft)
    DB.saveData("battery_1", int(BATTERY_PERCENTAGE))
    DB.saveData("battery_2", BATTERY_LEFT)

def checkTemp():
    global CPU_TEMP
    path = '/sys/class/thermal/thermal_zone0/temp'
    with open(os.path.join(os.path.dirname(__file__), path), 'r') as input_file:
        temp = float(input_file.read())
        tempB = temp/1000
        if CPU_TEMP != tempB:
            CPU_TEMP = tempB
            DB.saveData("cpu_temp", CPU_TEMP)
def run():
    checkTemp()
    checkBattery()

if __name__ == "__main__":
    run()