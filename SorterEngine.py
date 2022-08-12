from os import system as run
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from time import sleep as wait
from difflib import SequenceMatcher
from picamera import piCamera
import pytesseract as OCR
import pigpio

#set up Card class with details of the current card
class Card:
    def __init__(self, picture_path):
        self.image = Image.open(picture_path).crop((250, 320, 2960, 1630))
        self.name = ""
        self.valid = False
        self.detect()

    #prepares image to be readable by OCR
    def prepare_image(self):
        self.image = ImageEnhance.Brightness(self.image).enhance(1.5)
        self.image = ImageEnhance.Color(self.image).enhance(0)
        self.image = ImageEnhance.Sharpness(self.image).enhance(2)
        self.image = ImageEnhance.Contrast(self.image).enhance(4)

    #takes text read from card and compares it with names in database to find the most probable card
    def match_card(self, reading):
        same = [0, 0]
        matcher = SequenceMatcher(None, "", reading)
        for name in names:
            matcher.set_seq1(name)
            similarity = round(matcher.ratio(), 5)
            if similarity > same[1]:
                same = [name, similarity]
        self.name = same[0]
        self.similarity = same[1]
        
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

#preheat camera
cam = PiCamera()
cam.resolution = (3280, 2464)
cam.start_preview()

#prepare card database
names, properties = [], []
with open("CardsList.txt", "r", encoding = "utf8") as CardsList:
    for line in CardsList.readlines():
        line = line.split("%")
        names.append(line[0].lower())
        properties.append(line[1].split("|"))
        properties[-1][-1] = properties[-1][-1][:-1].split(";")

#prepare GPIO
Pin = pigpio.pi()
Pin_enable = 6
X_step = 26
X_dir = 21
Y_step = 19
Y_dir = 20
Pin_col = 22
Pin_val = 27
Pin_ed = 17
Pin_reset = 14
Pin_start = 2

for pin in [Pin_ed, Pin_col, Pin_val, Pin_reset, Pin_start]:
    Pin.set_mode(pin, pigpio.INPUT)
for pin in [Pin_enable, X_step, Y_step, X_dir, Y_dir]:
    Pin.set_mode(pin, pigpio.OUTPUT)

#define movement methods
def move_x(direction, distance):
    Pin.write(X_dir, direction)
    for temp in range(distance):
        Pin.write(X_step, 1)
        wait(0.042)
        Pin.write(X_step, 0)
        wait(0.042)
        
def move_y(direction, distance):
    Pin.write(Y_dir, direction)
    for temp in range(distance):
        Pin.write(Y_step, 1)
        wait(0.042)
        Pin.write(Y_step, 0)
        wait(0.042)

def pos_reset():
    Pin.write(Pin_enable, 0)
    while not Pin_reset.read():
        move_x(0, 16)
    Pin.write(Pin_enable, 1)

#last variables' initiation
end = False
stacks = []
stacklength = 6950 #(distance to cover / distance per revolution) * steps per revolution
rnat = 0

#wait for button press
while not Pin.read(Pin_start):
    pass
wait(1)

#loop until last card or second button press
while not end and not Pin.read(Pin_start):
    
    #take the card picture and prepare it for detection
    picture_path = "/home/pi/Desktop/card.jpg"
    cam.capture(picture_path)
    card = Card(picture_path)

    #if valid, find its stack
    if card.valid:
        stacknum = 0
        not_this = True
        if len(stacks) > 0:
            for stack in stacks:
                not_this = False
                if Pin.read(Pin_col):
                    if stack[0] == card.properties[0]:
                        pass
                    else:
                        not_this = True
                if Pin.read(Pin_val):
                    if stack[1] == card.properties[1]:
                        pass
                    else:
                        not_this = True
                if Pin.read(Pin_ed):
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
            stacks.append(card.properties)
        elif len(stacks) == 25 and not_this:
            stacks.append("leftover")

    #in case card is not readable enough, leftover stack it is
    else:
        stacknum = 25
        
    #go to the correct position and drop off the card
    Pin.write(Pin_enable, 0)
    move_x(stacknum>rnat, abs(stacknum-rnat)*stacklength)
    move_y(stacknum%2, 256)
    Pin.write(Pin_enable, 1)
