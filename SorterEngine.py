from os import system as run
from PIL import Image, ImageEnhance, ImageFilter
from time import sleep as wait
from difflib import SequenceMatcher
import pytesseract as OCR

#set up Card class with details of the current card
class Card:
    def __init__(self, picture_path):
        self.image = Image.open(picture_path)
        self.name = ""
        self.valid = False
        self.detect()

    #prepares image to be readable by OCR
    def prepare_image(self):
        for x in range(5):
            self.image = self.image.filter(ImageFilter.SHARPEN)
        self.image = self.image.filter(ImageFilter.GaussianBlur)

    #takes text read from card and compares it with names in database to find the most probable card
    def match_card(self, reading):
        same = [0, 0]
        matcher = SequenceMatcher(None, "", reading)
        for name in names:
            matcher.set_seq1(name)
            similarity = round(matcher.ratio(), 5)
            if similarity > same[1]:
                same = [name, similarity]
        print(reading, same)
        self.name = same[0]
        
    #card detection method - detects text and fetches card's values
    def detect(self):
        global end
        self.valid = False
        self.prepare_image()
        self.name = OCR.image_to_string(self.image).lower().replace("\n", " ")
        if self.name.replace(" ", "") == "end":
            end = True
        elif self.name.replace(" ", "") == "":
            pass
        else:
            self.match_card(self.name)
            self.properties = properties[names.index(self.name)]
            self.valid = True
           
#prepare card database
names, properties = [], []
with open("CardsList.txt", "r", encoding = "utf8") as CardsList:
    for line in CardsList.readlines():
        line = line.split("%")
        names.append(line[0].lower())
        properties.append(line[1].split("|"))
        properties[-1][-1] = properties[-1][-1][:-1].split(";")

#get going
end = False
stacks = []
props = input("Properties?(0 = color, 1 = mana value, 2 = edition): ")
while not end:
        #take the card picture and prepare it for detection
        picture_path = input("name: ").replace(" ", "_").lower() + ".jpg"
        card = Card(picture_path)
        if card.valid:
            #grab the user-chosen categories to compare
            categories = []
            for cat in map(int, props):
                categories.append(card.properties[cat])
            if "2" in props:
                editions = True
            else:
                editions = False
                
            #find the stack to drop card on
            stacknum = 0
            not_this = True
            if len(stacks) > 0:
                for stack in stacks:
                    not_this = False
                    for x in range(len(categories) - editions):
                        if stack[x] == card.properties[x]:
                            pass
                        else:
                            not_this = True
                    if editions:
                        edition_intersect = [edition for edition in card.properties[-1] if edition in stack[-1]]
                        if len(edition_intersect) > 0:
                            stack[-1] = edition_intersect
                        else:
                            not_this = True
                    if not_this and stacknum < 24:
                        stacknum += 1
                    else:
                        break
                
            #remember new stack
            if len(stacks) < 25 and not_this:
                stacks.append(categories)
            elif len(stacks) == 25 and not_this:
                stacks.append("leftover")
                
            #find out the position to go to and drop off the card
            position = stacknum

        #in case card is not readable enough, drop it in the leftover bin
        else:
            position = 25
        print(position, stacks[position])
