import os
import math
import ipinfo
from datetime import datetime as dt
from babel.dates import format_date

# check json file is older than 1 hour


def is_file_older_than(file, delta):
    cutoff = dt.utcnow() - delta
    mtime = dt.utcfromtimestamp(os.path.getmtime(file))
    if mtime < cutoff:
        return True
    return False
# compare 2 times older than delta


def is_time_older_than(time, delta):
    print(dt.utcnow() - time, delta)
    if (dt.utcnow() - time) > delta:
        return True
    return False
# get city name from ipinfo.io


def getCity():
    access_token = '16cb61bf42b6e4'
    handler = ipinfo.getHandler(access_token)
    details = handler.getDetails()
    return details.city

### timestamp converter to get current date tor each cell ########


def convertTimestamp(value):
    dt_object = dt.fromtimestamp(value)
    date = format_date(dt_object, locale='tr')
    return str(date)

### timestamp converter to get day name ########


def getDayName(value):
    days = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cts", "Pzr"]
    dt_object = dt.fromtimestamp(value)
    return days[dt_object.weekday()]


def text2int(textnum, numwords={}):
    if not numwords:
        units = [
            "sıfır", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz",
            "dokuz", "on", "onbir", "oniki", "onüç", "ondört", "onbeş", "onaltı", "onyedi", "onsekiz", "ondokuz"
        ]

        tens = ["", "", "yirmi", "otuz", "kırk",
                "elli", "atmış", "yetmiş", "seksen", "doksan"]

        scales = ["yüz", "bin", "milyon", "milyar", "trilyon"]

        numwords["and"] = (1, 0)
        for idx, word in enumerate(units):
            numwords[word] = (1, idx)
        for idx, word in enumerate(tens):
            numwords[word] = (1, idx * 10)
        for idx, word in enumerate(scales):
            numwords[word] = (0, 10 ** (idx * 3 or 2))

    current = result = 0
    for word in textnum.split():
        if word not in numwords:
            return False

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0
    final = result+current

    length = int(math.log10(final)+1)
    if int(length) == 1:
        final = '0'+str(final)
    return final


print(text2int("iki"))
