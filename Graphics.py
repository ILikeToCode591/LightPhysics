import pygame
import pygame as pg


class NineSliced:
    widthError = ValueError('width is too low')
    heightError = ValueError('length is too low')

    def __init__(self, baseImage: pg.surface.Surface, slices: tuple[int, int, int, int]):

        self.baseImage = baseImage
        self.left, self.right, self.top, self.bottom = self.slices = slices
        self.centre = (self.left, self.top, baseImage.get_width() - self.right, baseImage.get_height() - self.bottom)
        self.parts = {}

        self.createParts()

    def createParts(self):

        horizontals = (0, self.centre[0], self.centre[2], self.baseImage.get_width())
        verticals = (0, self.centre[1], self.centre[3], self.baseImage.get_height())
        self.parts.clear()

        for v in range(len(verticals) - 1):
            for h in range(len(horizontals) - 1):
                surface = pg.surface.Surface((horizontals[h + 1] - horizontals[h], verticals[v + 1] - verticals[v]),
                                             pg.SRCALPHA)

                surface.blit(self.baseImage, (0, 0),
                             (horizontals[h], verticals[v], horizontals[h + 1], verticals[v + 1]))

                self.parts[len(self.parts)] = surface.copy()

    def createImage(self, width, height, scale=1) -> pygame.surface.Surface:

        if width < self.baseImage.get_width():
            raise self.widthError
        if height < self.baseImage.get_height():
            raise self.heightError

        horizontalResize = width - (self.left + self.right) * scale
        verticalResize = height - (self.top + self.bottom) * scale

        horizontals = (0, self.left * scale, width - self.right * scale)
        verticals = (0, self.right * scale, height - self.bottom * scale)

        image = pg.surface.Surface((width, height), pg.SRCALPHA)
        part = 0

        for v in range(len(verticals)):
            for h in range(len(horizontals)):
                image.blit(pg.transform.scale(self.parts[part], (
                    horizontalResize if h % 2 else self.parts[part].get_width() * scale,
                    verticalResize if v % 2 else self.parts[part].get_height() * scale)), (horizontals[h], verticals[v]))
                part += 1

        return image


class Text:

    def __init__(self, text, color, position, size):

        self.font = pg.font.Font('assets/fonts/game_over.ttf', size)
        self.text = text
        self.color = color
        self.image = self.font.render(text, True, color)
        self.rect = self.image.get_rect()
        self.position = position

        self.rect.topleft = position

    def draw(self, screen: pg.surface.Surface):
        screen.blit(self.image, self.rect)

    def updateText(self, text=None, color=None):
        self.text = text if text is not None else self.text
        self.color = color if color else self.color

        self.image = self.font.render(self.text, True, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = self.position


class TextInput:
    allInstances = []

    def __init__(self, position, plate, selectedPlate, width, height, title, scale = 1):

        self.nineSliced = plate
        self.selectedSliced = selectedPlate
        self.name = Text(title, (200, 200, 200), position, 32*scale)
        self.position = position

        self.plate = plate.createImage(width, height)
        self.selectedPlate = selectedPlate.createImage(width + 2, height + 2, 2)
        self.plateRect = self.plate.get_rect()
        self.selectedPlateRect = self.selectedPlate.get_rect()

        self.plate = pg.transform.scale(self.plate, (self.plateRect.width/2, self.plateRect.height/2))
        self.selectedPlate = pg.transform.scale(self.selectedPlate,
                                                (self.selectedPlateRect.width/2, self.selectedPlateRect.height/2))
        self.plateRect = self.plate.get_rect()
        self.selectedPlateRect = self.selectedPlate.get_rect()

        self.selectedPlateRect.topleft = self.plateRect.topleft = self.name.rect.bottomleft
        self.input = Text('', (0, 0, 0), self.plateRect.center, 32 * scale)

        self.selected = False

        TextInput.allInstances.append(self)

    def changeText(self, text, bypass=False):
        if self.input.rect.width + 10 > self.plateRect.width and not bypass:
            return
        self.input.updateText(text)

    def drawSelector(self, screen):
        screen.blit(self.selectedPlate, self.selectedPlateRect)

    def updatePosition(self, position):
        self.name.position = position
        self.name.updateText()

        self.selectedPlateRect.topleft = self.plateRect.topleft = self.name.rect.bottomleft
        self.input.position = self.plateRect.center
        self.input.updateText()

    def draw(self, screen):
        screen.blit(self.plate, self.plateRect)
        if self.selected:
            self.drawSelector(screen)
        self.input.draw(screen)
        self.name.draw(screen)

    @staticmethod
    def drawInstances(screen, draw):
        for inp in TextInput.allInstances:
            screen.blit(inp.plate, inp.plateRect)
            if inp.selected:
                inp.drawSelector(screen)


class Button:

    allInstances = []

    def __init__(self, position, size, plateActive, plateInactive, icon, function):

        self.plateActive = plateActive
        self.plateInactive = plateInactive

        self.imageActive = self.plateActive.createImage(*size, 2)
        self.imageInactive = self.plateInactive.createImage(*size, 2)

        self.image = self.imageInactive

        self.rect = self.imageActive.get_rect()

        self.position = position
        self.icon = icon
        self.iconRect = self.icon.get_rect()
        self.function = function

        self.iconRect.center = self.rect.center = self.position

        self.activated = False
        self.hidden = False

        Button.allInstances.append(self)

    def activate(self):
        self.activated = True
        self.image = self.imageActive

    def deactivate(self, *args):
        self.activated = False
        self.image = self.imageInactive
        self.function(*args)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        screen.blit(self.icon, self.iconRect)

    def setPosition(self, position):
        self.position = position
        self.iconRect.center = self.rect.center = self.position

    def kill(self):
        Button.allInstances.remove(self)
        del self

    @staticmethod
    def drawInstances(screen):
        for button in Button.allInstances:
            if not button.hidden:
                button.draw(screen)

    @staticmethod
    def checkInteraction():
        for button in Button.allInstances:
            if button.rect.collidepoint(pg.mouse.get_pos()) and not button.hidden:
                button.activate()
                return button
        return None

class KeyBind:
    def __init__(self):
        pass




