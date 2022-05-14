from asyncio import exceptions
import json
import queue
import sys

import sounddevice as sd
import speech_recognition as sr
# from vosk import Model, KaldiRecognizer


# speech recognition start
recognizer = sr.Recognizer()
microphone = sr.Microphone()
for index, name in enumerate(sr.Microphone.list_microphone_names()):
    print("Microphone with name \"{1}\" found for `Microphone(device_index={0})`".format(index, name))

def listen_google():
    # It takes microphones recognition from the user and returns String output
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source, phrase_time_limit=3)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='tr-TR')
        return query
    except Exception as e:
        # print(e)
        return False


        
# WAKE_WORD = "robot"
# # Vosk Speech To text start
# liste = queue.Queue()
# modelEN = Model("robot/assets/model-en")
# modelTR = Model("robot/assets/model-tr")


# def callback(indata, frames, time, status):
#     if status:
#         print(status, file=sys.stderr)
#     liste.put(bytes(indata))


# def wakeup():
#     with sd.RawInputStream(
#             samplerate=16000,
#             blocksize=8000,
#             dtype='int16',
#             channels=1,
#             callback=callback):
#         rec = KaldiRecognizer(modelTR, 16000)
#         print("uyandırma bekleniyor...")
#         while True:
#             data = liste.get()
#             if len(data) == 0:
#                 break
#             if rec.AcceptWaveform(data):
#                 # print(rec.PartialResult())
#                 result = json.loads(rec.Result())['text']
#                 list = [word for word in result.split()]
#                 if WAKE_WORD in list:
#                     return True
#         return False


# def listen():
#     print("komut bekleniyor...")
#     with sd.RawInputStream(
#             samplerate=32000,
#             blocksize=8000,
#             dtype='int16',
#             channels=1,
#             callback=callback):
#         rec = KaldiRecognizer(modelTR, 32000)
#         while True:
#             data = liste.get()
#             if rec.AcceptWaveform(data):
#                 result = json.loads(rec.Result())['text']
#                 if result != "":
#                     # eğer liste olarak geri donecekse
#                     # return [word for word in result.split()]
#                     # eger tek satır string olarak dönecekse
#                     return result
#                 break
#         return False


# vosk speech to text end




# main task execution

# while True:
#     print(listen_google())
