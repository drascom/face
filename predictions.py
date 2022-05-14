import json
import re
import os
import random
from ..config.definitions import ROOT_DIR

# Load JSON data


def load_json(file):
    with open(file) as bot_responses:
        print("Cevaplar yüklendi!")
        return json.load(bot_responses)


# Store JSON data
response_data = load_json(os.path.join(ROOT_DIR, "assets", "bot.json"))


def random_string():
    random_list = [
        "Lütfen biraz açıklar mısın ?.",
        "Ne söylediğini anlamadım",
        "Rica etsem tekrar eder misin ?",
        "Çok özür dilerim duyamadım.",
        "bunu bilmiyorum."
    ]

    list_count = len(random_list)
    random_item = random.randrange(list_count)

    return {"type": "err", "text": random_list[random_item]}


def get_response(input_string):
    split_message = re.split(r'\s+|[,;?!.-]\s*', input_string.lower())
    print("[TAHMIN] gelen: ", split_message)
    score_list = []

    # Check all the responses
    for response in response_data:
        response_score = 0
        required_score = 0
        required_words = response["required_words"]

        # Check if there are any required words
        if required_words:
            for word in split_message:
                if word in required_words:
                    required_score += 1

        # Amount of required words should match the required score
        if required_score == len(required_words):
            # print(required_score == len(required_words))
            # Check each word the user has typed
            for word in split_message:
                # If the word is in the response, add to the score
                if word in response["msg"]:
                    response_score += 1

        # Add score to list
        score_list.append(response_score)
        # Debugging: Find the best phrase
        # print(response_score, response["msg"])

    # Find the best response and return it if they're not all 0
    best_response = max(score_list)
    response_index = score_list.index(best_response)

    # Check if input is empty
    if input_string == "":
        return "Konuşmak için birşeyler söylemen lazım"

    # If there is no good response, return a random one.
    if best_response >= 1:
        # next line answer text only
        # return response_data[response_index]["bot_response"]
        # this line returns full body of predicted answer
        return response_data[response_index]

    return random_string()


if __name__ == "__main__":
    from config.definitions import ROOT_DIR
    while True:
        msg = input("Kullanıcı: ")
        print("Robot:", get_response(msg))
