import GlobalVariables
from GlobalVariables import *
import GlobalVariables as gVars
from Mirror import Mirror
from Pointer import Pointer
from Particles import ParticleGenerator
from SaveAndLoad import SaveAndLoad

SCREEN = pg.display.set_mode((winWidth, winHeight), pg.SRCALPHA)

TIME = pg.time.Clock()

objects = [Pointer, Mirror]
selectedObject = None
selectedInput = None
selectedButton = None
transforming = False

pressedKeys = []

gameEnd = False

SaveAndLoad.load(gVars.currentSave)

for i in range(len(objects)):
    objects[i].objectButton.setPosition(pg.Vector2(60 + 110 * i, winHeight - 35))

while not gameEnd:

    # event checking
    for event in pg.event.get():

        if event.type == pg.MOUSEBUTTONDOWN:

            selectedButton = Button.checkInteraction()

            if selectedObject:

                for opt in selectedObject.options:
                    if opt[0].plateRect.collidepoint(*pg.mouse.get_pos()):
                        if selectedInput is not None:
                            selectedInput.selected = False

                        selectedInput = opt[0]
                        selectedInput.changeText('')
                        selectedInput.selected = True
                        break
                else:
                    if selectedInput is not None:
                        selectedInput.selected = False
                    selectedInput = None

                if selectedInput:
                    break

            if event.button == pg.BUTTON_LEFT:
                for cl in objects:
                    selectedObject = cl.checkCollision(pg.Vector2(pg.mouse.get_pos()))[1]
                    if selectedObject:
                        for k in GlobalVariables.BUILDTOOLS:
                            k.hidden = False

                        for opt in selectedObject.options:
                            opt[0].changeText(opt[1]())
                        break
                else:
                    for k in GlobalVariables.BUILDTOOLS:
                        k.hidden = True

                    selectedObject = None
                    transforming = False

            if event.button == pg.BUTTON_RIGHT and selectedObject:
                transforming = True

        if event.type == pg.MOUSEBUTTONUP:
            if event.button == pg.BUTTON_RIGHT and transforming and selectedObject:
                transforming = False
            if selectedButton:
                selectedButton.deactivate()
                selectedButton = None

        if event.type == pg.MOUSEWHEEL:
            if gVars.MODE == 'load':
                SaveAndLoad.scroll(event.y)

        if event.type == pg.KEYDOWN:

            KeyBind.updateInteraction(event.key, True)
            pressedKeys.append(event.key)

            if event.key == pg.K_d and selectedObject:
                if isinstance(selectedObject, Mirror):
                    selectedObject = Mirror(selectedObject.body.position, selectedObject.body.rotation, selectedObject.body.length)
                elif isinstance(selectedObject, Pointer):
                    selectedObject = Pointer(selectedObject.body.position, selectedObject.body.rotation, selectedObject.body.width, selectedObject.color)

            if pg.K_s == event.key and pg.key.get_mods() & pg.KMOD_CTRL:
                SaveAndLoad.save(gVars.currentSave)

            if selectedInput:
                if event.key == pg.K_BACKSPACE:
                    selectedInput.changeText(selectedInput.input.text[:-1], True)
                elif event.key == pg.K_RETURN:
                    if selectedObject:
                        selectedObject.updateOptions(selectedInput)
                    selectedInput.selected = False
                    selectedInput = None
                else:
                    selectedInput.changeText(selectedInput.input.text + event.unicode)

            else :
                if event.key in MODES:
                    gVars.MODE = MODES[event.key]
                    for cl in objects:
                        cl.resetInstances()

                if gVars.MODE != 'build':

                    for k in GlobalVariables.BUILDTOOLS:
                        k.hidden = True

                    for obj in objects:
                        obj.objectButton.hidden = True

                    if pg.K_ESCAPE in pressedKeys:
                        gVars.MODE = 'build'
                        if selectedInput:
                            selectedInput.input.updateText('', (0, 0, 0))
                            selectedInput = None
                else:

                    if selectedObject:
                        for k in GlobalVariables.BUILDTOOLS:
                            k.hidden = False

                    if len(SaveAndLoad.availableSaves):
                        for button, delet in SaveAndLoad.availableSaves:
                            button.kill()
                            delet.kill()
                        SaveAndLoad.availableSaves.clear()
                    for obj in objects:
                        obj.objectButton.hidden = False

                SaveAndLoad.newSave.hidden = True if gVars.MODE != 'load' else False
                gVars.lightingButton.hidden = False if gVars.MODE == 'simulate' else True

        if event.type == pg.KEYUP:
            KeyBind.updateInteraction(event.key, False)
            pressedKeys.remove(event.key)

        # checking for game quit
        if event.type == pg.QUIT:
            gameEnd = True

    # drawing background
    SCREEN.fill(bgColor)

    if gVars.MODE == 'simulate':
        for cl in [ParticleGenerator] + objects:
            cl.drawInstances(SCREEN, True)
        gVars.lightingButton.draw(SCREEN)

    elif gVars.MODE == 'build':

        if selectedObject:
            if pg.K_RIGHT in pressedKeys:
                selectedObject.body.rotate(-0.1)
            if pg.K_LEFT in pressedKeys:
                selectedObject.body.rotate(0.1)
            if pg.K_UP in pressedKeys:
                selectedObject.increaseSize()
            if pg.K_DOWN in pressedKeys:
                selectedObject.reduceSize()

            for opt in selectedObject.options:
                if selectedInput != opt[0]:
                    opt[0].changeText(opt[1]())
                opt[0].draw(SCREEN)

            if pg.K_DELETE in pressedKeys:
                selectedObject.kill()
                selectedObject = None

        if transforming:
            selectedObject.body.move(pg.Vector2(*pg.mouse.get_pos()))

        for cl in objects:
            cl.drawInstances(SCREEN, False)

        Button.drawInstances(SCREEN)

    elif gVars.MODE == 'newSave':

        if selectedInput != SaveAndLoad.saveName:
            selectedInput = SaveAndLoad.saveName

        if pg.K_RETURN in pressedKeys:
            if SaveAndLoad.addSave(selectedInput.input.text):
                gVars.MODE = 'build'
                selectedInput.input.updateText('', (0, 0, 0))
                selectedInput = None
            else:
                selectedInput.input.updateText(color=(255, 0, 0))

        transparentBG.fill((bgColor+(80,)))

        SCREEN.blit(transparentBG, (0,0))
        SaveAndLoad.saveName.draw(SCREEN)

    elif gVars.MODE == 'load':
        if not len(SaveAndLoad.availableSaves):
            SaveAndLoad.loadSaves()

        Button.drawInstances(SCREEN)

    GlobalVariables.enterKeyBind.hidden = True if gVars.MODE != 'newSave' else False

    KeyBind.drawInstances(SCREEN)

    pg.display.flip()

    TIME.tick(24)

pg.quit()
