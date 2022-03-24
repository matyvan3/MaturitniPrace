from PIL import Image, ImageEnhance, ImageOps

class Card:
    def __init__(self, img_path):
        self.image = Image.open(img_path)
        self.width, self.height = self.image.size
        self.cropcolor()
        self.cardcolor = self.colorcode("color")
        self.croprarity()
        self.cardrarity = self.colorcode("rarity")
        self.cutout = self.image

    def cropcolor(self):
        self.cutout = self.image.crop((150, 50, 940, 150))
        self.width, self.height = self.cutout.size

    def croprarity(self):
        self.cutout = self.image.crop((975, 920, 1100, 980))
        self.width, self.height = self.cutout.size

    def cropedition(self):
        self.cutout = ImageEnhance.Contrast(self.image.crop((69, 1525, 142, 1555))).enhance(5)
        self.width, self.height = self.cutout.size
        self.cutout = self.cutout.resize((self.width*2, self.height*2))
        self.width, self.height = self.cutout.size
        
    def colorcode(self, mode):
        pixels = self.cutout.getdata()
        red = green = blue = y = 0
        size = len(pixels)
        for i in range(self.height):
            x = 0
            for j in range(self.width):
                position = y * self.width + x
                pixel = pixels[position]
                if mode == "color":
                    if pixel[0] > 80 or pixel[1] > 80 or pixel[2] > 80:
                        red += pixel[0]
                        green += pixel[1]
                        blue += pixel[2]
                    else:
                        size -= 1
                elif mode == "rarity":
                    if round(100*pixel[0]/(pixel[1]+1)) in range(round(100*self.cardcolor[0]/self.cardcolor[1])-10, round(100*self.cardcolor[0]/self.cardcolor[1])+10) and round(100*pixel[1]/(1+pixel[2])) in range(round(100*self.cardcolor[1]/self.cardcolor[2])-10, round(100*self.cardcolor[1]/(1+self.cardcolor[2]))+10) and round(100*pixel[2]/pixel[0]) in range(round(100*self.cardcolor[2]/self.cardcolor[0])-10, round(100*self.cardcolor[2]/self.cardcolor[0])+10):
                        size -= 1
                    elif pixel[0] > 200 and pixel[1] > 200 and pixel[2] > 200:
                        size -= 1
                    else:
                        red += pixel[0]
                        green += pixel[1]
                        blue += pixel[2]
                else:
                    pass
                x += 1
            y += 1
        red = round(red / size)
        green = round(green / size)
        blue = round(blue / size)
        return (red, green, blue)

    def color(self):
        red, green, blue = self.cardcolor
        if green in range(round(red*0.85), round(red*0.95)) and blue in range(round(red*0.45), round(red*0.7)):
            return ("multicolor")
        elif green in range(round(red*0.7), round(red*0.8)) and blue in range(round(red*0.65), round(red*0.75)):
            return ("red")
        elif green in range(round(red*1.05), round(red*1.3)) and blue in range(round(red*1), round(red*1.1)):
            return ("green")
        elif green in range(round(red*0.925), round(red*1.025)) and blue in range(round(red*0.925), round(red*1.08)) and blue <= 172:
            return ("black")
        elif green in range(round(red*0.98), round(red*1.05)) and blue in range(round(red*0.95), round(red*1.125)) and blue >= red:
            return ("colorless")
        elif green in range(round(red*0.975), round(red*1.025)) and blue in range(round(red*0.925), round(red*1.025)):
            return("white")
        elif green in range(round(red*1.05), round(red*1.2)) and blue in range(round(red*1.15), round(red*1.7)):
            return("blue")
        else:
            return ("TBA")

    def rarity(self):
        red, green, blue = self.cardrarity
        if green in range(round(red*0.5), round(red*0.75)) and blue + 10 < green:
            return ("mythic")
        elif green in range(round(red*0.85), round(red*1.05)) and blue in range(round(red*0.4), round(red*0.65)):
            return ("rare")
        elif green in range(round(red*1.05), round(red*1.2)) and blue in range(round(red*1.1), round(red*1.3)) and red < 150:
            return ("uncommon")
        else:
            return ("common")

    def getedition(self):
        self.cropedition()
        ImageOps.invert(self.cutout).convert("1").save("edition.jpg")
        self.editionsymbol = list(ImageOps.invert(self.cutout).convert("1").getdata())

    def parsesymbol(self):
        symbol = []
        for pixel in self.editionsymbol:
            symbol.append(str(pixel))
        return symbol

    def tryshifts(self, previous, symbol, width):
        prev = previous.copy()
        symb = symbol.copy()
        for i in range(round(len(previous)/width)):
            for j in range(width):
                symb.append(symb.pop(j))
            if self.compare(prev, symb):
                return True
            else:
                pass
        return False

    def compare(self, previous, symbol):
        same = 0
        size = 0
        for i in range(len(previous)):
            if previous[i] == symbol[i] and symbol[i] == "0":
                same += 1.0
            else:
                pass
            if symbol[i] == "0":
                size += 1
        if same/size >= 0.75:
            return True
        else:
            if same/size >= 0.6:
                print(same/size)
            return False
               
    def edition(self):
        self.getedition()
        try:
            with open("editions.txt", "x"):
                pass
        except:
            pass
        with open("editions.txt", "r+") as editions:
            x = 0
            symbol = self.parsesymbol()
            lines = editions.readlines()
            self.editioncount = len(lines)
            for edition in lines:
                previous = edition.split(", ")
                previous.append(previous.pop(-1)[:-2])
                if self.compare(previous, symbol):
                    break
                elif self.tryshifts(previous, symbol, self.width):
                    break
                else:
                    x += 1
        if self.editioncount == x:
            with open("editions.txt", "a") as editions:
                editions.write(", ".join(symbol) + "\n")
        return x