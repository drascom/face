import json
import pickle
import re
import os
import nltk
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from rich.console import Console
from keras.models import load_model

lemmatizer = WordNetLemmatizer()
intents = json.load(open("json/intents.json", encoding="utf-8"))

words = pickle.load(open("models/model_nltk/words.pkl", "rb"))  # nosec
classes = pickle.load(open("models/model_nltk/classes.pkl", "rb"))  # nosec
types = pickle.load(open("models/model_nltk/types.pkl", "rb"))  # nosec
model = load_model("models/model_nltk/chatbotmodel.h5")

console = Console()

stop_words = list(set(stopwords.words("turkish")))


def remove_punctuation(sentence):
    sentence = re.sub(r"[^\w\s]", "", sentence)
    return sentence


def remove_stopword(sentence):
    return [w for w in sentence if w not in stop_words]


# Turkish lemmatizer return list->tuple->list item need to convert to string
# def clean_lemmatizer_result(raw_word):
#     return raw_word[0][1][0].replace("[", "").replace("]", "")


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence, language='turkish')
    # for english
    sentence_words = [lemmatizer.lemmatize(
        word.lower()) for word in sentence_words]
    return sentence_words


def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)


def predict_class(sentence):
    bow = bag_of_words(sentence)
    result_of_model = model.predict(np.array([bow]))[0]
    error_threshold = 0.25
    results = [[i, r]
               for i, r in enumerate(result_of_model) if r > error_threshold]
    results.sort(key=lambda x: x[1], reverse=True)
    print("[TAHMIN] bulunanlar: ")
    if sentence != "":
        for r in results:
            print(classes[r[0]])
        return [
            {
                "intent": classes[r[0]],
                "probability": str(r[1]),
                "type_of_intent": types[r[0]],
            }
            for r in results
            if r[1] > 0.50
        ]
    return [
        {
            "intent": "no_answer",
        }
    ]


def get_response(intents_list, intents_json, msg):
    try:
        tag = intents_list[0]["intent"]
        list_of_intents = intents_json["intents"]
        for i in list_of_intents:
            if i["tag"] == tag:
                print("[PREDICTION] best guess: ", i["tag"])
                return i
        return False
    except IndexError:
        print("[TAHMIN] istek bulunamadı!")
        return False


def run(command):
    if command != "" and command is not False:
        print("1. istek alındı")
        predicted_list = predict_class(command)
        return get_response(predicted_list, intents, command)
    return False


def cls():
    os.system("cls" if os.name == "nt" else "clear")


if __name__ == "__main__":
    cls()
    while True:
        message = input("> ")
        res = run(message)
        console.print(res)
