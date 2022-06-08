import wikipedia
import pprint


class AskWiki:
    def __init__(self, request):
        self.request = request
        self.response = ""
        self.get_data()

    def get_data(self):
        wikipedia.set_lang("tr")
        self.request = self.request.replace(" ", "+")
        try:
            # suggest = wikipedia.suggest(self.request)
            # summary = wikipedia.summary(self.request, sentences=6)
            page = wikipedia.page(self.request).content
            prefix, success, result = page.partition("==")
            self.response = prefix
        except wikipedia.PageError as err:
            self.response = {
                "error": f"Sayfa bulunamadı",
            }
        except wikipedia.DisambiguationError as err:
            self.response = {
                "error": f"çok fazla sonuç bulundu",
            }

        return self.response


if __name__ == "__main__":
    print(AskWiki("araba").response)
    # pp = pprint.PrettyPrinter(indent=4)
    # x = AskWiki("serik")
    # pp.pprint(x.response)
