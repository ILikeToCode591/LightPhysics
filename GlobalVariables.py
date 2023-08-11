import math

from Graphics import *

# initializing pygame
pg.init()

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
keyboardUnpressed = NineSliced(pg.image.load('assets/textures/nineSlices/KeyBoard.png'), (5, 5, 4, 12))
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

lightingButton = Button((winWidth - 42, 42), (64, 64), *goldenButtonPreset, bulbLit, None)
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

keyWidth, keyHeight = keyDims = 50, 50
gridH, gridV = winWidth // keyWidth, winHeight // keyHeight
keyOffset = 0


def createKeyBind(key, name, gridx, gridy, gridSpanX=1, gridSpanY=1):
    posx = winWidth - (keyOffset + keyWidth * (gridH - gridx + 1)) if gridx > gridH // 2 else keyOffset + keyWidth * (
                gridx - 1)
    posy = winHeight - (
                keyOffset + keyHeight * (gridV - gridy + 1)) if gridy > gridV // 2 else keyOffset + keyHeight * (gridy)

    return KeyBind(key, name,
                   (keyWidth * gridSpanX, keyHeight * gridSpanY),
                   pg.Vector2((posx, posy))
                   )


enterKeyBind = createKeyBind(pg.K_RETURN, 'Enter', gridH // 2 + 1, gridV // 2 + 4, 2)

MODEKEYS = (
    createKeyBind(pg.K_b, 'B', gridH, 3),
    createKeyBind(pg.K_s, 'S', gridH, 4),
    createKeyBind(pg.K_l, 'L', gridH, 5)
)

BUILDTOOLS = (
    createKeyBind(pg.K_RIGHT, '>', gridH, gridV),
    createKeyBind(pg.K_DOWN, 'v', gridH - 1, gridV),
    createKeyBind(pg.K_LEFT, '<', gridH - 2, gridV),
    createKeyBind(pg.K_UP, '^', gridH - 1, gridV - 1),
    createKeyBind(pg.K_d, 'D', gridH - 4, gridV),
    createKeyBind(pg.K_DELETE, 'Delete', 2.2, gridV-0.75, gridSpanX=2),
)

for k in BUILDTOOLS:
    k.hidden = True


def getID():
    global availableIDs

    id = availableIDs.pop(0)
    availableIDs = list(range(availableIDs[0], availableIDs[0] + 11))

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
        options[i][0].updatePosition((max(options[i - 1][0].name.rect.right, options[i - 1][0].plateRect.right) + 30 +
                                      options[i][0].name.rect.width / 2 if i > 0 else 10 + options[i][
            0].name.rect.width / 2, 10))
