import random, sys, time

"""
Text adventure engine
"""

# constants
NORTH = 1
SOUTH = -1
EAST = 2
WEST = -2
dirToStr = {NORTH: "north", SOUTH: "south", EAST: "east", WEST: "west"}

# death messages
deathMsgs = {
    "suicide": "You decided to end it all.",
    "unknown": "You have died of dysentery.",
    "fell": "You took a long walk off a short cliff.",
    "drowned": "You tried to breathe underwater.",
    "squashed": "You were turned into a pancake.",
    "bleeding": "You bled out.",
    "explosion": "You were blowed to smitheroons.",
    "burned": "You were baked for 20 minutes or until golden brown.",
    "pit": "You've fallen, and you can't get up.",
    "win": "A strange game, this is. The only winning move is not to play.",
    "spike": "You were turned into a kebab."
}

# declare some globals
playerRoom = None
inventory = []
score = 0
alive = True

# synonyms
synRoom = ["room", "place", "here", "around"]
synPlayer = ["self", "player", "me", "myself"]
synScore = ["points", "score"]
synGet = ["get", "pickup", "take", "grab"]
synDie = ["kms", "die", "suicide"]
synPit = ["pit", "into pit", "in pit"]

# Helper functions
def getArticle(string):
    return "an" if string.lower()[0] in "aeiou" else "a"

def die(cause = "unknown"):
    global alive
    alive = False
    print(deathMsgs[cause])
    print("GAME OVER\nFinal Score: {0}".format(score))

def checkDirValid(direction):
    if playerRoom.directionDict[direction]:
        playerRoom.directionDict[direction].enter()
    else:
        print("You can't go {0}.".format(dirToStr[direction]))
# Classes
class Room:
    def __init__(self, name = "Room", desc = "A room.", north = None, east = None, south = None, west = None, items = None):
        self.name = name
        self.desc = desc
        self.items = items if items else [] # If items is not None, use it, else use []. Fixes a bug that would cause items dropped in one empty room to appear in all empty rooms
        self.directionDict = {NORTH: north, EAST: east, SOUTH: south, WEST: west}
        for key in self.directionDict:
            if self.directionDict[key] != None: # Are we linking to a room?
                # Does that room link to us?
                if self.directionDict[key].directionDict[-key] == None:
                    # If not, make a link.
                    self.directionDict[key].directionDict[-key] = self

    def enter(self):
        # Enter a room. This also handles leaving the other room.
        global playerRoom
        playerRoom = self
        self.look()

    def look(self):
		# Give a description of the room. Used when looking around and entering the room.
        print('\n' + self.name.upper())
        print(self.desc)

        goString = "\nYou can go: "
        gSLen = len(goString)
        for key in self.directionDict:
            if self.directionDict[key] != None:
                goString += "\n" + dirToStr[key]
        if len(goString) > gSLen: # lol hax, is there a better way to do this?
            print(goString)

        itemString = "\nYou can see: "
        iSLen = len(itemString)
        for item in self.items:
            itemString += "\n" + item.name
        if len(itemString) > iSLen:
            print(itemString)

    def linkRoom(self, room, direction):
        # For dynamic linking of rooms
        if self.directionDict[direction] != None:
            # We already have a room here!
            raise Exception("Room {0} already has a {1}ward exit!".format(self.name, dirToStr[direction]))
        elif room.directionDict[-direction] != None:
            # We use a seperate if statement here to use room's name
            raise Exception("Room {0} already has a {1}ward exit!".format(room.name, dirToStr[-direction]))
        else:
            self.directionDict[direction] = room
            room.directionDict[-direction] = self

    def unlinkRoom(self, direction, destroyOther = True):
        # To facilitate one-way doors or destroy exits based on player action
        if self.directionDict[direction] == None:
            # We don't have a room here!
            return
        else:
            self.directionDict[direction] = None
            if destroyOther: room.directionDict[-direction] = None

class Item:
    # Base class for items.
    def __init__(self, name = "Item", desc = "An item."):
        self.name = name
        self.desc = desc
    def pickUp(self):
        print("Picked up {0} {1}.".format(getArticle(self.name), self.name))
        playerRoom.items.remove(self)
        inventory.append(self)
    def drop(self):
        print("Dropped the {0}.".format(item.name))
        inventory.remove(self)
        playerRoom.items.append(self)

class Ruby(Item):
    # Gives points.
    def __init__(self, name = "ruby", desc = "A shiny red gem.", value = 5):
        Item.__init__(self, name, desc)
        self.value = value
    def pickUp(self):
        global score
        Item.pickUp(self)
        score += self.value
        print("Got {0} points.".format(self.value))
    def drop(self):
        global score
        Item.drop(self)
        score -= self.value
        print("Lost {0} points.".format(self.value))

class Pit(Item):
    # You fall down these.
    def __init__(self, name = "pit", desc = "A hole. You can't see the bottom of it."):
        Item.__init__(self, name, desc)

    def pickUp(self):
        print("You can't pick up a pit.") # is not possible

    def drop(self):
        print("How did you even get a pit?")
        die()

class Weapon(Item):
    # Wepon
    def __init__(self, name = "weapon", desc = "A weapon.", dmg = 1):
        Item.__init__(self, name, desc)
        self.dmg = 1

# Room declarations
firstRoomDesc = """You are in a small room about 20ft by 20ft with an opening on each side. In the middle, there is a rugged looking knight sitting back against the wall, wearing only ragged robes and a helmet, with a broken sword next to him."""
firstRoom = Room(desc = firstRoomDesc, items = [Ruby(), Ruby()])

westRoom1Desc = """The room is small and dark. There are only a few candles surrounding a gaping, almost endless looking pit. Inside the pit it feels cold and damp, but there is a light at the end of the tunnel."""
westRoom1 = Room(name = "West Room", desc = westRoom1Desc, east = firstRoom, items = [Pit()])

eastRoom1Desc = """There is a small chest on the back wall, guarded by a knight in shining white solid crusader armor holding a massive bloodied battle axe."""
eastRoom1 = Room(name = "East Room", desc = eastRoom1Desc, west = firstRoom)

# intro
print("Welcome to Hale! You need to pick a class.\n")
time.sleep(3)
playerClass = input("Type any class you want.\n> ")
print("Your {0} is going to be great!\n".format(playerClass))
time.sleep(3)
print("Now that you're {0} {1}, you're going to need a weapon.\n".format(getArticle(playerClass), playerClass))
playerWeapon = input("What weapon would you like?\n>")
inventory.append(Weapon(name = playerWeapon))
print("Your {0} seems pretty cool, but I've seen better.\n".format(playerWeapon))
time.sleep(3)
print("Now that you're {0} {1} and you have your {2}, you're ready to begin your adventure in Hale.\n".format(getArticle(playerClass), playerClass, playerWeapon))
time.sleep(3)

# Go into the first room at the start
firstRoom.enter()

#Command parser
while alive:
    command = input("> ").lower().split(" ", 1)
    # To aid in readability
    verb = command[0]
    obj = command[1] if len(command) > 1 else None
    if verb == "look":
        if obj: # Do we have an obj?
            if obj[:3] == "at ": # does it start with "at "?
                obj = obj[3:] #cut off the "at ".
        if not obj or obj in synRoom:
            playerRoom.look()
        elif obj in synPlayer:
            print("Looking good.")
        else:
            # It might be an item.
            foundItem = False
            for item in playerRoom.items + inventory:
                if obj == item.name.lower():
                    print(item.desc)
                    foundItem = True
                    break
            if not foundItem: print("Look where now?")
    elif verb == "go":
        if obj == "north":
            checkDirValid(NORTH)
        elif obj == "south":
            checkDirValid(SOUTH)
        elif obj == "east":
            checkDirValid(EAST)
        elif obj == "west" or obj == "weast":
            checkDirValid(WEST)
        elif obj in synPit:
            fell = False
            for obj in playerRoom.items:
                if isinstance(obj, Pit):
                    die("pit")
                    fell = True
                    break
            if not fell:
                print("You don't see a pit.")
        elif obj:
            print("You can't go " + command[1] + ".")
        else:
            print("Go where?")
    elif verb == "north":
        checkDirValid(NORTH)
    elif verb == "south":
        checkDirValid(SOUTH)
    elif verb == "east":
        checkDirValid(EAST)
    elif verb == "west" or verb == "weast":
        checkDirValid(WEST)
    elif verb in synScore:
        print("Your current score is {0}.".format(score))
    elif verb == "inventory":
        iString = "You have: "
        if len(inventory) == 0:
            print("You have nothing.")
        else:
            for item in inventory:
                iString += "\n" + item.name
            print(iString)
    elif verb in synGet:
        if not obj:
            print("Get what?")
        else:
            gotItem = False
            for item in playerRoom.items:
                if item.name.lower() == obj:
                    item.pickUp()
                    gotItem = True
                    break
            if not gotItem: print("You don't see {0} {1}.".format(getArticle(obj), obj))
    elif verb == "drop":
        dropped = False
        for item in inventory:
            if item.name.lower() == obj:
                dropped = True
                item.drop()
                break
        if not dropped:
            print("Drop what?" if not obj else "You don't have {0} {1}." .format(getArticle(obj), obj))
    elif verb in synDie:
        die("suicide")
        break
    elif verb == "win":
        die("win")
        break
    elif verb == "jump":
        if obj in synPit: # seperate statement so we can expand the "jump" verb later
            fell = False
            for obj in playerRoom.items:
                if isinstance(obj, Pit):
                    die("pit")
                    fell = True
                    break
            if not fell:
                print("You don't see a pit.")
    elif verb:
        print("You don't know how to {0}.".format(verb))
    else:
        print("Type in a command.")
