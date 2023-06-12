import GlobalVariables
import Pointer

from Polygon import Rectangle
from Graphics import *
from GlobalVariables import *


class Mirror:
    allInstances = []
    objectButton = Button(
        pg.Vector2(0, 0),
        (100, 50),
        *goldenButtonPreset,
        pg.image.load('assets/textures/icons/Mirror.png'),
        lambda: Mirror((winWidth / 2, winHeight / 2), 0, 100)
    )

    def __init__(self, position, rotation, length):

        self.id = GlobalVariables.getID()

        self.body = Rectangle(pg.Vector2(*position), rotation, 3, length, (171, 196, 170))

        self.reflectedRays = []

        self.options = (
            (
                TextInput((10, 10), whiteBordered, selectedGold, 80, 32, 'Rotation'),
                lambda: str(math.degrees(self.body.rotation))[:5],
                lambda x: isClass(x, float),
                lambda x: self.body.rotate(
                    math.radians(float(x)) - self.body.rotation
                )

            ),
            (
                TextInput((90, 10), whiteBordered, selectedGold, 64, 32, 'Pos: x'),
                lambda: str(self.body.position.x)[:3],
                lambda x: isClass(x, float),
                lambda x: self.body.move(
                    pg.Vector2(float(x), self.body.position.y)
                )
            ),
            (
                TextInput((170, 10), whiteBordered, selectedGold, 64, 32, 'Pos: y'),
                lambda: str(self.body.position.y)[:3],
                lambda x: isClass(x, float),
                lambda x: self.body.move(
                    pg.Vector2(self.body.position.x, float(x))
                )
            ),
            (
                TextInput((250, 10), whiteBordered, selectedGold, 64, 32, 'Length'),
                lambda: str(self.body.length)[:3],
                lambda x: isClass(x, float),
                lambda x: adjustSize(self, x, self.body.length)
            )
        )
        organizeOptions(self.options)

        Mirror.allInstances.append(self)

    def interact(self, ray, colpos):
        rotation = self.body.rotation * 2 - ray.rotation
        newRay = Pointer.Laser(self, colpos, rotation, ray.color, ray.laserWidth, True)

        self.reflectedRays.append(newRay)

        if GlobalVariables.lightupSimulation:
            self.fixLighting()

        return True

    def fixLighting(self):
        for ray in self.reflectedRays:
            offset = self.body.angleVector * 4
            pos = False
            neg = False
            for comparer in self.reflectedRays:
                if (ray.origin + offset - comparer.origin).magnitude() < 1:
                    pos = True
                if (ray.origin - offset - comparer.origin).magnitude() < 1:
                    neg = True
                if pos and neg:
                    ray.lighting = False

    def increaseSize(self):
        self.body.length += 2
        self.body.update()

    def reduceSize(self):
        if self.body.length - 2 < 10:
            return False
        self.body.length -= 2
        self.body.update()

        return True

    def update(self, screen, draw):
        if len(self.reflectedRays) and not self.body.vibrating:
            self.body.vibrating = True
        elif not len(self.reflectedRays) and self.body.vibrating:
            self.body.vibrating = False

        self.body.draw(screen)

        if not draw:
            return

        for ray in self.reflectedRays:
            ray.rayCast(screen)

    def updateOptions(self, selectedInput):
        for opt in self.options:
            if selectedInput == opt[0] and opt[2](selectedInput.input.text):
                opt[3](selectedInput.input.text)

    def getSaveOptions(self):
        return (self.body.position.x, self.body.position.y), self.body.rotation, self.body.length

    def kill(self):
        Mirror.allInstances.remove(self)
        del self

    @staticmethod
    def checkCollision(point):
        for mirror in Mirror.allInstances:
            if mirror.body.checkCollisions(point):
                return True, mirror
        return False, None

    @staticmethod
    def drawInstances(screen, draw=True):
        for mirror in Mirror.allInstances:
            mirror.update(screen, draw)

    @staticmethod
    def resetInstances():
        for mirror in Mirror.allInstances:
            for ray in mirror.reflectedRays:
                ray.kill()
            mirror.reflectedRays.clear()