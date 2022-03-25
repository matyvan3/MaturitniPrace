from os import system as run
from PIL import Image
from colorrec import Card
from time import sleep as wait
import pigpio, picamera

#set up GPIO pins
pins = pigpio.pi()

pin_on = 26
pin_color = 17
pin_rarity = 27
pin_edition = 22
pins_input = [pin_on, pin_color, pin_rarity, pin_edition]

pin_m1_dir = 5
pin_m1_go = 6
pin_m2_dir = 13
pin_m2_go = 12
pins_output[pin_m1_dir, pin_m2_dir, pin_m1_go, pin_m2_go]

for pin in pins_input:
    pins.set_mode(pin, pigpio.INPUT)

for pin in pins_output:
    pins.set_mode(pin, pigpio.OUTPUT)

#resetting position to 0
def resetPosition():
    pins.write(pin_m2_dir, 1)
    while pin_reset != 1:
        for x in range(16):
            pins.write(pin_m2_go, 1)
            wait(0.0005)
            pins.write(pin_m2_go, 0)
            wait(0.0005)
    rnat = 0

#get a list for storing values of all the card stacks
stacks = []

#method for dropping to the correct stack
def drop(position):
    if position > rnat:
        pins.write(pin_m2_dir, 0)
    elif position < rnat:
        pins.write(pin_m2_dir, 1)
    else:
        pass
    for x in range(512*(position-rnat)): #1 slot size times number of spots
        for y in range(200): #1/16 of rotation
            pins.write(pin_m2_go, 1)
            wait(0.0005)
            pins.write(pin_m2_go, 0)
            wait(0.0005)
    for x in range(8):
        for y in range(200):
            pins.write(pin_m1_go, 1)
            wait(0.0005)
            pins.write(pin_m1_go, 0)
            wait(0.0005)
    rnat = position
    
#prepare camera
cam = picamera.PiCamera()
cam.start_preview()

#wait until initiated
resetPosition()
while pins.read(pin_on) == 0:
    pass

#get going
end = False
while pins.read(pin_on) == 0 or not end:
        #take the card picture and prepare it for detection
        picture_path = r"/home/pi/Desktop/pic.jpg"
        cam.capture(picture_path)
        Image.open(picture_path).resize(size = (1600, 1200), box = (0, 0, 3280, 2343)).save(picture_path)
        card = Card(picture_path)

        #grab the user-chosen categories to compare
        categories = []
        if pins.read(pin_color) == 1:
            categories.append(card.color())
        else:
            pass
        if pins.read(pin_rarity) == 1:
            categories.append(card.rarity())
        else:
            pass
        if pins.read(pin_edition) == 1 and len(categories) != 2:
            categories.append(card.edition())
        else:
            pass
        
        if pins.read(pin_color) == 1 and (pins.read(pin_rarity) == 1 or pins.read(pin_edition) == 1) and categories[0] in ["colorless", "multicolor"]:
            categories[0] = "nonbasic"
            
        #find the stack to drop card on
        stacknum = 0
        for stack in stacks:
            this_one = True
            for x in range(len(categories)):
                if stack[x] == categories[x]:
                    pass
                else:
                    this_one = False
                    break
            if not this_one and stacknum < 24:
                stacknum += 1
            else:
                break
        
        #remember new stack
        if len(stacks) < 25 and not this_one:
            stacks.append(categories)
            
        #find out the position to go and side to drop off the card
        pins.write(pin_m1_dir, stacknum % 2)
        position = round((stacknum - side) / 2)
        drop(position)

#stop preview to stop wasting power
cam.stop_preview()
