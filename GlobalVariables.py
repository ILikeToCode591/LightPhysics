from Graphics import *
import pygame as pg
import math

winWidth = 1000
winHeight = 700
pi = math.pi

bgColor = (26, 26, 26)

currentSave = open('assets/Latest_Save.txt', 'r').read()

lightupSimulation = True

bulbLit = pg.image.load('assets/textures/icons/Bulb_lit.png')
bulbUnlit = pg.image.load('assets/textures/icons/Bulb_unlit.png')

greyBevel = NineSliced(pg.image.load('assets/textures/nineSlices/GreyBevel.png'), (6, 6, 6, 6))
whiteBordered = NineSliced(pg.image.load('assets/textures/nineSlices/whiteBordered.png'), (6, 6, 6, 6))
selectedGold = NineSliced(pg.image.load('assets/textures/nineSlices/selectedGold.png'), (7, 7, 7, 7))
keyboardUnpressed = NineSliced(pg.image.load('assets/textures/nineSlices/KeyBoard.png'), (5, 5, 3, 13))
keyboardPressed = NineSliced(pg.image.load('assets/textures/nineSlices/KeyBoard_Pressed.png'), (5, 5, 7, 9))

goldenButtonPreset = (
    NineSliced(
            pg.image.load('assets/textures/nineSlices/goldenButtonActive.png'),
            (5, 5, 5, 5)
        ),
    NineSliced(
            pg.image.load('assets/textures/nineSlices/goldenButtonInactive.png'),
            (5, 5, 5, 5)
        )
)

lightingButton = Button((winWidth-42, 42), (64, 64), *goldenButtonPreset, bulbLit, None)
lightingButton.hidden = True

def toggleLighting():

    global lightupSimulation, lightingButton

    lightupSimulation = not lightupSimulation

    lightingButton.icon = bulbLit if lightupSimulation else bulbUnlit
    lightingButton.iconRect = lightingButton.icon.get_rect()

    lightingButton.iconRect.center = lightingButton.position


lightingButton.function = lambda: toggleLighting()

MODES = {
    pg.K_b: 'build',
    pg.K_s: 'simulate',
    pg.K_l: 'load'
}

MODE = 'build'

transparentBG = pg.surface.Surface((winWidth, winHeight), pg.SRCALPHA)

availableIDs = list(range(10))


def getID():
    global availableIDs

    id = availableIDs.pop(0)
    availableIDs = list(range(availableIDs[0], availableIDs[0]+11))

    return id


def setMode(mode):
    global MODE
    MODE = mode


def isClass(num, cls):
    try:
        cls(num)
        return True
    except ValueError:
        return False


def adjustSize(obj, value, relative):
    if int((float(value) // 1 - relative) / 2) > 0:
        for i in range(int((float(value) - relative) / 2)):
            obj.increaseSize()
    else:
        for i in range(-int((float(value) - relative) / 2)):
            if not obj.reduceSize():
                break


def organizeOptions(options):
    for i in range(len(options)):
        options[i][0].updatePosition((max(options[i-1][0].name.rect.right, options[i-1][0].plateRect.right)+30+options[i][0].name.rect.width/2 if i>0 else 10+options[i][0].name.rect.width/2, 10))


