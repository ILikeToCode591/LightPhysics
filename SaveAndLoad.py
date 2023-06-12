import pickle
from os import listdir, remove

import GlobalVariables as gVars
from GlobalVariables import *
from Graphics import *
from Mirror import Mirror
from Pointer import Pointer

pg.init()

OBJECTS = {
    'Pointer': Pointer,
    'Mirror': Mirror
}


class SaveAndLoad:
    availableSaves = []
    saveName = TextInput((winWidth / 2 - 75, winHeight / 2 - 32), whiteBordered, selectedGold, 300, 64,
                         'Model Name: ',
                         2)
    newSave = Button(
        (
            (winWidth // 2),
            (0)
        ),
        (150, 80),
        *goldenButtonPreset,
        Text('NewSave', (0, 0, 0), (0, 0), 64).image,
        lambda: gVars.setMode('newSave')
    )
    newSave.hidden = True

    @staticmethod
    def load(saveFile):

        for obj in OBJECTS.values():
            for ob in obj.allInstances:
                ob.kill()
            obj.allInstances.clear()

        try:
            file = open(f'assets/saves/{saveFile}.dat', 'rb')
        except FileNotFoundError:
            savesFolder = listdir('assets/saves/')
            if not len(savesFolder):
                SaveAndLoad.addSave('New_Save')
                file = open(f'assets/saves/New_Save.dat', 'rb')
            else:
                file = open(f'assets/saves/{savesFolder[0]}', 'rb')

        while True:
            try:
                savedObj = pickle.load(file)
            except EOFError:
                break

            OBJECTS[savedObj[0]](*savedObj[1])

        for button, delete in SaveAndLoad.availableSaves:
            button.kill()
            delete.kill()
        SaveAndLoad.availableSaves.clear()
        gVars.MODE = 'build'
        for obj in Pointer, Mirror:
            obj.objectButton.hidden = False

        SaveAndLoad.newSave.hidden = True

    @staticmethod
    def save(saveFile):

        if not saveFile.isidentifier():
            return False

        file = open(f'assets/saves/{saveFile}.dat', 'wb')
        for obj in OBJECTS:
            for inst in OBJECTS[obj].allInstances:
                pickle.dump(
                    [
                        obj,
                        inst.getSaveOptions()
                    ],
                    file
                )

        with open('assets/Latest_Save.txt', 'w') as latest:
            latest.write(saveFile)

        file.close()

        return True

    @staticmethod
    def addSave(saveFile):
        if not saveFile.isidentifier():
            return False

        file = open(f'assets/saves/{saveFile}.dat', 'wb')

        with open('assets/Latest_Save.txt', 'w') as latest:
            latest.write(saveFile)

        file.close()

        gVars.currentSave = saveFile
        SaveAndLoad.load(saveFile)

        return True

    @staticmethod
    def deleteSave(save):
        remove(f'assets/saves/{save}')
        SaveAndLoad.loadSaves()

    @staticmethod
    def loadSaves():
        for button, delet in SaveAndLoad.availableSaves:
            button.kill()
            delet.kill()
        SaveAndLoad.availableSaves.clear()

        files = listdir('assets/saves/')
        trash = pg.image.load('assets/textures/icons/Trash.png')
        vert = 10

        for i in range(len(files)):
            icn = Text(files[i].split('.')[0].title(), (0, 0, 0), (0, 0), 64).image
            buttonWidth, buttonHeight = buttonDims = (icn.get_width() + 40, icn.get_height() + 30)

            SaveAndLoad.availableSaves.append((
                Button(
                    (
                        (buttonWidth / 2 + 10),
                        (buttonHeight / 2 + vert)
                    ),
                    buttonDims,
                    *goldenButtonPreset,
                    icn,
                    lambda x=files[i].split('.')[0]: SaveAndLoad.load(x)
                ),
                Button(
                    (
                        winWidth - trash.get_width() / 2 - 20,
                        buttonHeight / 2 + vert
                    ),
                    (
                        trash.get_width() + 20,
                        buttonHeight
                    ),
                    *goldenButtonPreset,
                    trash,
                    lambda x=files[i]: SaveAndLoad.deleteSave(x)
                )
            )
            )

            vert += buttonHeight + 10
        else:
            SaveAndLoad.newSave.setPosition(pg.Vector2(winWidth / 2, (SaveAndLoad.newSave.rect.height / 2 + vert)))
            SaveAndLoad.newSave.hidden = False

    @staticmethod
    def scroll(amount):

        amount*=10

        if (amount > 0 and SaveAndLoad.availableSaves[0][0].rect.y - 10 < 0) or \
                (amount < 0 and SaveAndLoad.newSave.rect.y + SaveAndLoad.newSave.rect.height + 10 > winHeight):
            for button, delete in SaveAndLoad.availableSaves:
                button.setPosition(button.position + pg.Vector2(0, amount))
                delete.setPosition(delete.position + pg.Vector2(0, amount))
            SaveAndLoad.newSave.setPosition(SaveAndLoad.newSave.position + pg.Vector2(0, amount))
