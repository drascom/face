import re
import pprint
import wikipediaapi


def remove_punctuation(sentence):
    sentence = re.sub(r"[^\w\s]", "", sentence)
    return sentence


# def remove_stopword(sentence):
#     return [w for w in sentence if w not in stop_words]


class Wikipedia:
    def __init__(self, request):
        self.request = request
        self.response = ""
        self.get_data()

    def get_data(self):
        wiki_wiki = wikipediaapi.Wikipedia("tr")
        self.request = self.request.replace(" ", "+")
        result = wiki_wiki.page(self.request)
        if result.summary:
            # textCutIndex =result.summary[0:300].rindex('.')
            # self.response = result.summary[0:textCutIndex]
            self.response = result.summary
        else:
            self.response = {
                "error": f"bilgi bulunamadı",
            }
        return self.response


if __name__ == "__main__":
    x = Wikipedia("atatürk")
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(x.response)
