from os import system as run
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from time import sleep as wait
from difflib import SequenceMatcher
from picamzero import Camera
import pytesseract as OCR
import RPi.GPIO as GPIO
import json

#set up Card class with details of the current card
class Card:
    def __init__(self, picture_path):
        self.image = Image.open(picture_path)#.crop((250, 320, 2960, 1630))
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
        for name in list(cards):
            matcher.set_seq1(name)
            similarity = round(matcher.ratio(), 5)
            if similarity > same[1]:
                same = [name, similarity]
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
            self.properties = cards[self.name][0]
            self.valid = True
            
    def fits(self, stack):
        for parameter in list(stack.keys()):
            if parameter in ["colorIdentity", "colors", "types", "supertypes"] and stack[parameter] in self.properties[parameter]:
                pass
            elif parameter == "convertedManaCost" and stack[parameter] != "7+" and self.properties[parameter][0] == stack[parameter]:
                pass
            elif parameter == "convertedManaCost" and stack[parameter] == "7+" and float(self.properties[parameter]) >= 7:
                pass
            elif parameter == "legalities" and self.properties[parameter][stack[parameter]] == "Legal":
                pass
            else:
                return 0
        return 1

#preheat camera
cam = Camera()
cam.resolution = (3280, 2464)
cam.start_preview()
picture_path = "/home/user/Desktop/test.jpg"

#prepare card values
with open("AtomicCards.json", "r", encoding = "utf8") as file:
    cards = json.load(file)["data"]

#prepare GPIO
pinDict = {}
slotDistance = 69
with open("config.txt", "r") as pinList:
    for pinTemp in pinList.readlines():
        pin = pinTemp.split(";")
        if pin[0] == "steps":
            slotDistance = (pin[1])
        elif pin != []:
            pinDict[pin[0]] = int(pin[1])
        else:
            pass

for pin in [pinDict.get(pin) for pin in ["hstop", "vstops", "end"]]:
    GPIO.setup(pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
    
for pin in [pinDict.get(pin) for pin in ["enable", "pump", "light", "hstep", "hdir", "vstep", "vdir"]]:
    GPIO.setup(pin, GPIO.OUT)

#ease picking a state of a GPIO output
level = [GPIO.LOW, GPIO.HIGH]

#define movement methods
def move_h(stack):
    global slotDistance
    GPIO.output(pinDict["hdir"], level[1])
    hpwm = GPIO.PWM(pinDict["hstep"], slotDistance*2)
    hpwm.start(40)
    wait(stack/2)
    hpwm.stop()
        
def reset_h():
    GPIO.output(pinDict["hdir"], level[0])
    hpwm = GPIO.PWN(pinDict["hdir"], 128)
    hpwm.start(40)
    while not GPIO.input(pinDict["hstop"]):
        pass
    hpwm.stop()
    
def move_v(direction):
    GPIO.output(pinDict["hdir"], level[direction])
    vpwm = GPIO.PWM(pinDict["vstep"], 512)
    vpwm.start(40)
    wait(0.3)
    while not GPIO.input(pinDict["vstops"]):
        pass
    wait(0.05)
    vpwm.stop()

def drop_card():
    move_v(0)
    GPIO.output(pinDict["pump"], level[1])
    wait(2)
    GPIO.output(pinDict["pump"], level[0])

#load stacks selection
os.run("python3 SlotSetup.py")
with open("stacks.json", "r", encoding = "utf8") as file:
    stacks = json.load(file)

#loop until last card or second button press
while not end and not GPIO.input(pinDict["end"]):
    
    #reset position and find the first card
    move_v(1)
    reset_h()
    move_v(0)
    
    #take the card picture and prepare it for detection
    cam.take_photo(picture_path)
    card = Card(picture_path)

    #if valid, find its stack
    if card.valid:
        not_this = True
        for stacknum in range(8):
            if card.fits(stacks[str(stacknum)]) or stacknum == 7:
                break
            else:
                pass

    #in case card is not readable enough, leftover stack it is
    else:
        stacknum = 7
        
    #go to the correct position and drop off the card
    move_v(1)
    move_h(stackNum)
    drop_card()