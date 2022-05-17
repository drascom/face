# from Alarm import RecordAlarm
# from Weather import Weather
# from Clock import Clock
# from Wikipedia2 import AskWiki
from os import listdir
from os.path import dirname
__all__ = [i[:-3] for i in listdir(dirname(__file__)) if not i.startswith('__') and i.endswith('.py')]