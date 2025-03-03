import json
from tkinter import *

try:
    with open("stacks.json", "r", encoding = "utf8") as file:
        slots = json.load(file)
except:
    slots = {}
    for x in range(8):
        slots[str(x)] = {}

parameters = {"colorIdentity" : ["B", "G", "R", "U", "W"], "colors" : ["B", "G", "R", "U", "W"], "manaValue" : [0,1,2,3,4,5,6,"7+"], "legalities" : ["commander", "duel", "legacy", "modern", "oathbreaker", "penny", "vintage"], "types" : ["Artifact", "Battle", "Creature", "Enchantment", "Instant", "Land", "Planeswalker", "Sorcery"], "supertypes" : ["Basic", "Legendary", "Snow", "World"]}
currentSlot, currentParameter = 0,""

def slot_select():
    global currentSlot
    currentSlot = int(slot.curselection()[0]) + 1
    slot.pack_forget()
    slotButton.pack_forget()
    parameter.pack()
    parameterButton.pack()
    doneButton.pack_forget()
    label.configure(text = "Pick a parameter for slot " + str(currentSlot))
    
def parameter_select():
    global currentParameter
    currentParameter = parameter.get(parameter.curselection()[0])
    parameter.pack_forget()
    parameterButton.pack_forget()
    for x in range(choice.size()):
        choice.delete(0)
    for opt in parameters[currentParameter]:
        choice.insert("end", opt)
    choice.pack()
    choiceButton.pack()
    label.configure(text = "Pick a choice for parameter: " + currentParameter)
    

def choice_select():
    global currentSlot, currentParameter
    slots[str(currentSlot - 1)] = {currentParameter : str(choice.get(choice.curselection()[0]))}
    slot.delete(currentSlot-1)
    slot.insert(currentSlot-1, currentParameter + ": " + str(choice.get(choice.curselection()[0])))
    choice.pack_forget()
    choiceButton.pack_forget()
    slot.pack()
    slotButton.pack()
    doneButton.pack()
    label.configure(text = "Pick a slot to edit:")

def sae():
    with open("stacks.json", "w+", encoding = "utf8") as file:
        json.dump(slots, file)
    root.destroy()

root = Tk()
root.title("Card sorting setup")
root.geometry("400x400")
label = Label(root, text = "Pick a slot to edit:")
label.pack()
slot = Listbox(root)
for x in range(8):
    slot.insert(x+1, x+1)
slot.pack()
slotButton = Button(root, text = "Edit this slot", command = slot_select)
slotButton.pack()
parameter = Listbox(root)
params = list(parameters.keys())
for x in range(len(params)):
    parameter.insert(x+1, params[x])
parameterButton = Button(root, text = "Select this parameter", command = parameter_select)
choice = Listbox(root)
choiceButton = Button(root, text = "Select this value", command = choice_select)
doneButton = Button(root, text = "Save and exit", command = sae)
root.mainloop()