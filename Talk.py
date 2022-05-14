import os
import audioplayer
import threading
import requests
from pydub import AudioSegment
import pyttsx3
from gtts import gTTS
import espeakng


# def greet_thread(word):
#     tts_thread = threading.Thread(target=greet, args=[word])
#     tts_thread.start()


# def greet(word):
#     tts = gTTS(text=word, lang="es")
#     tts.save("words.mp3")
def speeding():
    in_path = 'sound/sound_out/input.mp3'
    ex_path = 'sound/sound_out/output.mp3'
    sound = AudioSegment.from_file(in_path)
    slower_sound = speed_swifter(sound, 1.2)
    slower_sound.export(ex_path, format="mp3")


def speed_swifter(sound, speed=1.0):
    sound_with_altered_frame_rate = sound._spawn(
        sound.raw_data, overrides={"frame_rate": int(sound.frame_rate * speed)})
    return sound_with_altered_frame_rate


def playFile(filename):
    audioplayer.AudioPlayer(filename).play(block=True)


def speak_pyttsx3(context):
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 170)  # konuşma hızı
        voices = engine.getProperty("voices")
        print("ses sayısı: ", voices)
        if len(voices) > 69:
            engine.setProperty("voice", voices[69].id)
        else:
            engine.setProperty("voice", voices[1].id)
        engine.say(context)
        engine.runAndWait()
        return True
    except Exception as e:
        print(e)
        print("Free Pttsx3 çalışmıyor")
        return False


def speak_espeak(context):
    try:
        speaker = espeakng.Speaker()
        speaker.voice = "tr"
        speaker.wpm = 180
        speaker.pitch = 80
        speaker.say(context, wait4prev=True)
        return True
    except Exception as e:
        print(e)
        print("Free Espeak çalışmıyor")
        return False


def speak_local(context):
    # Save audio file
    try:
        speech = gTTS(text=context, lang="tr", slow=False)
        speech.save("sound/sound_out/input.mp3")
        speeding()
        playFile("sound/sound_out/output.mp3")
        os.remove("sound/sound_out/input.mp3")
    except Exception as e:
        print(e)
        print("gTTS çalışmıyor")
        return False


def speak_online(context):
    try:
        voiceServer = "https://freetts.com/Home/PlayAudio"
        voiceServerParameters = {
            "Language": "tr-TR",
            "Voice": "tr-TR-Standard-D",
            "type": 0,
            "TextMessage": context,
        }
        # voiceServerParameters = {'Language': 'tr-TR', "Voice": "Filiz_Female", "type": 1,"TextMessage": context,"id":"Filiz"}
        x = requests.get(voiceServer, data=voiceServerParameters)
        speech_file = "https://freetts.com/audio/" + x.json()["id"]
        doc = requests.get(speech_file)
        with open("sound/sound_out/input.mp3", "wb") as f:
            f.write(doc.content)
        speeding()
        playFile("sound/sound_out/output.mp3")
        os.remove("sound/sound_out/input.mp3")
        return True
    except Exception as e:
        print(e)
        print("Free TTS çalışmıyor")
        return False


def say(context):
    # Play audio file
    # function = ""+str(engine)
    # eval(function)(context)
    # speak_pyttsx3(context)
    # speak_espeak(context)
    # speak_online(context)
    tts_thread = threading.Thread(
        target=speak_local, args=[context], daemon=True)
    tts_thread.start()
    tts_thread.join()
    print("bitti")


if __name__ == "__main__":
    context = "Bugün hava açık, 23 derece, hafif rüzgarlı.Dışarı çıkarken montunu almayı unutma."
    say(context)
  
