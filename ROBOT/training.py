import json
import pickle
import random
import os
import nltk
import numpy as np
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import SGD
from tqdm import tqdm
from snowballstemmer import TurkishStemmer


def cls():
    os.system("cls" if os.name == "nt" else "clear")


stemmer = TurkishStemmer()
lemmatizer = WordNetLemmatizer()  # English

intents = json.load(open("json/intents.json", encoding="utf-8"))
words = []
classes = []
types = []
documents = []
ignore_letters = ["?", "!", ".", ","]

for intent in tqdm(intents["intents"]):
    for pattern in intent["patterns"]:
        word_list = nltk.word_tokenize(pattern)
        words.extend(word_list)
        stem_word_list = [stemmer.stemWord(word.lower()) for word in pattern]
        words.extend(stem_word_list)
        documents.append((word_list, intent["tag"]))
        if intent["tag"] not in classes:
            classes.append(intent["tag"])
    types.append(intent["type"])


# words = [
#     lemmatizer.lemmatize(word.lower()) for word in words if word not in ignore_letters
# ]
words = sorted(set(words))

pickle.dump(words, open("models/model_nltk/words.pkl", "wb"))
pickle.dump(classes, open("models/model_nltk/classes.pkl", "wb"))
pickle.dump(types, open("models/model_nltk/types.pkl", "wb"))

training = []
output_empty = [0] * len(classes)

for document in tqdm(documents):
    bag = []
    word_patterns = document[0]
    word_patterns = [lemmatizer.lemmatize(
        word.lower()) for word in word_patterns]
    for word in words:
        # print("word: ", word)
        bag.append(1) if word in word_patterns else bag.append(0)

    output_row = list(output_empty)
    output_row[classes.index(document[1])] = 1
    training.append([bag, output_row])

random.shuffle(training)
training = np.array(training)

train_x = list(training[:, 0])
train_y = list(training[:, 1])

model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation="relu"))
model.add(Dropout(0.5))
model.add(Dense(64, activation="relu"))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation="softmax"))

sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss="categorical_crossentropy",
              optimizer=sgd, metrics=["accuracy"])

hist = model.fit(
    np.array(train_x), np.array(train_y), epochs=400, batch_size=5, verbose=1
)
model.save("models/model_nltk/chatbotmodel.h5", hist)
print("Done")