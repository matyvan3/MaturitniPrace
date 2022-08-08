from PIL import Image
import urllib.request, random
from io import BytesIO

codes = []
with open("SetCodes.txt", "r", encoding="utf8") as file:
    for code in file.readlines():
        codes.append(code[:-1])

for x in range(1000):
    setcode = codes[random.randint(0, len(codes)-1)]
    url = r"https://www.mtgpics.com/pics/big/" + setcode.lower() + r"/" + str(f"{random.randint(0, 150):03}") + r".jpg"
    try:
        urllib.request.urlretrieve(url, "testimages/testimage" + str(x) + ".jpg")
    except:
        pass
