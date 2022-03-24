from os import system as run
from PIL import Image
from colorrec import Card
from time import sleep as wait
import pigpio, smbus2, picamera

#set up GPIO pins
pins = pigpio.pi()
I2C = smbus2.SMBus(1)

pin_on = 0
pin_color = 1
pin_rarity = 2
pin_edition = 3
pins_input = [pin_on, pin_color, pin_rarity, pin_edition]

for pin in pins_input:
    pins.set_mode(pin, pigpio.INPUT)

for pin in pins_output:
    pins.set_mode(pin, pigpio.OUTPUT)

#get a list for storing values of all the card stacks
stacks = []

#prepare camera
cam = picamera.PiCamera()
cam.start_preview()

#wait until initiated
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
            pins.write(LED_color, 1)
        else:
            pass
        if pins.read(pin_rarity) == 1:
            categories.append(card.rarity())
            pins.write(LED_rarity, 1)
        else:
            pass
        if pins.read(pin_edition) == 1 and len(categories) != 2:
            categories.append(card.edition())
            pins.write(LED_edition, 1)
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
        side = stacknum % 2
        position = round((stacknum - side) / 2)
        
        #send the position and side to Arduino to move and wait for execution
        to_send = []
        for char in str(side) + str(position):
            to_send.append(ord(char))
        I2C.write_i2c_block_data(0x02, 0x00, to_send)
        wait(5)

#stop preview to stop wasting power
cam.stop_preview()