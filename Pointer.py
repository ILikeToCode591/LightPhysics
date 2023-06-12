from random import random

import GlobalVariables
import Mirror
from GlobalVariables import *
from Particles import ParticleGenerator
from Polygon import Rectangle


class Pointer:
    allInstances = []
    objectButton = Button(
        pg.Vector2(0, 0),
        (100, 50),
        *goldenButtonPreset,
        pg.image.load('assets/textures/icons/Pointer.png'),
        lambda: Pointer((winWidth / 2, winHeight / 2), 0)
    )

    def __init__(self, position: tuple[int | float], rotation: int | float, width=15, color=(255, 0, 0)) -> None:

        self.id = GlobalVariables.getID()

        self.color = pg.Color(*color)
        self.lasers = [
            Laser(self, pg.Vector2(0, 0), rotation, self.color, 1)
        ]

        self.body = Rectangle(pg.Vector2(*position), rotation, 15, 50, (4, 4, 20), [
            (
                self.lasers[0],
                lambda x: self.lasers[0].setAngle(x),
                [1, 0]
            )
        ])

        self.options = (
            [
                TextInput((0, 10), whiteBordered, selectedGold, 80, 32, 'Rotation'),
                lambda: str(math.degrees(self.body.rotation))[:5],
                lambda x: isClass(x, float),
                lambda x: self.body.rotate(
                    math.radians(float(x)) - self.body.rotation
                )

            ],
            [
                TextInput((0, 10), whiteBordered, selectedGold, 64, 32, 'Pos: x'),
                lambda: str(self.body.position.x)[:3],
                lambda x: isClass(x, float),
                lambda x: self.body.move(
                    pg.Vector2(float(x), self.body.position.y)
                )
            ],
            [
                TextInput((0, 10), whiteBordered, selectedGold, 64, 32, 'Pos: y'),
                lambda: str(self.body.position.y)[:3],
                lambda x: isClass(x, float),
                lambda x: self.body.move(
                    pg.Vector2(self.body.position.x, float(x))
                )
            ],
            [
                TextInput((0, 10), whiteBordered, selectedGold, 64, 32, 'Width'),
                lambda: str(self.body.width)[:3],
                lambda x: isClass(x, float),
                lambda x: adjustSize(self, x, self.body.width)
            ],
            [
                TextInput((0, 10), whiteBordered, selectedGold, 64, 32, 'Color R:'),
                lambda: str(self.color.r),
                lambda x: isClass(x, int) and 0 <= int(x) <= 255,
                lambda x: self.changeColor(x, 0)
            ],
            [
                TextInput((0, 10), whiteBordered, selectedGold, 64, 32, 'Color G:'),
                lambda: str(self.color.g),
                lambda x: isClass(x, int) and 0 <= int(x) <= 255,
                lambda x: self.changeColor(x, 1)
            ],
            [
                TextInput((0, 10), whiteBordered, selectedGold, 64, 32, 'Color B:'),
                lambda: str(self.color.b),
                lambda x: isClass(x, int) and 0 <= int(x) <= 255,
                lambda x: self.changeColor(x, 2)
            ],

        )
        organizeOptions(self.options)

        adjustSize(self, width, self.body.width)

        Pointer.allInstances.append(self)

    def increaseSize(self):

        laserL, laserR = Laser(self, pg.Vector2(0, 0), self.body.rotation, self.color, 1), Laser(self, pg.Vector2(0, 0), self.body.rotation, self.color,
                                                                                1)
        self.lasers.extend([laserL, laserR])
        widthDisp = (len(self.lasers) - 1) / self.body.width
        self.body.children.extend([(
            laserL,
            lambda x: laserL.setAngle(x),
            [1, -widthDisp]
        ),
            (
                laserR,
                lambda x: laserR.setAngle(x),
                [1, widthDisp]
            )]
        )

        for laser in self.lasers[:-6]:
            laser.lighting = False

        for i in range(len(self.body.children)):
            self.body.children[i][2][1] = 2*(i//2)/len(self.body.children) * math.copysign(1, self.body.children[i][2][1])

        self.body.width += 1
        self.body.rotate(0)

    def reduceSize(self):

        if len(self.lasers) == 1:
            return False
        self.lasers[-2].kill()
        self.lasers[-1].kill()
        self.body.children = self.body.children[:-2]
        self.lasers = self.lasers[:-2]

        for i in range(len(self.body.children)):
            self.body.children[i][2][1] = 2 * (i // 2) / len(self.body.children) * math.copysign(1,
                                                                                                 self.body.children[i][
                                                                                                     2][1])

        for laser in self.lasers[:-6]:
            laser.lighting = False
        for laser in self.lasers[-6:]:
            laser.lighting = True

        self.body.width -= 1
        self.body.update()

        return True

    def changeColor(self, val, index):
        color = list(self.color)[:3]
        color[index] = int(val)
        self.color.update(*color)
        for laser in self.lasers:
            laser.color = self.color

    def update(self, screen, draw):

        self.body.draw(screen)

        for laser in self.lasers:
            pg.draw.rect(screen, laser.color, (laser.origin, (2, 2)))
            if draw:
                if not self.body.vibrating:
                    self.body.vibrating = True
                laser.rayCast(screen)
            else:
                if self.body.vibrating:
                    self.body.vibrating = False

    def updateOptions(self, selectedInput):
        for opt in self.options:
            if selectedInput == opt[0] and opt[2](selectedInput.input.text):
                opt[3](selectedInput.input.text)

    def getSaveOptions(self):
        return (self.body.position.x, self.body.position.y), self.body.rotation, self.body.width, tuple(self.color)

    def kill(self):
        for laser in self.lasers:
            laser.kill()
        Pointer.allInstances.remove(self)
        del self

    @staticmethod
    def checkCollision(point):
        for mirror in Pointer.allInstances:
            if mirror.body.checkCollisions(point):
                return True, mirror
        return False, None

    @staticmethod
    def drawInstances(screen, draw=True):
        for pointer in Pointer.allInstances:
            pointer.update(screen, draw)

    @staticmethod
    def resetInstances():
        for pointer in Pointer.allInstances:
            for laser in pointer.lasers:
                laser.targetPos = None
                laser.medium = 1


class Laser:

    def __init__(self, parent, origin, angle, color, laserWidth=2, lighting = True):
        self.parent = parent
        self.prvsParentID = None
        self.rotation = angle
        self.origin = origin
        self.laserWidth = laserWidth

        self.brightness = 4

        self.color = color

        self.rayVector = pg.Vector2(math.cos(self.rotation), -math.sin(self.rotation))

        self.particleGen = ParticleGenerator(self.color, 2, 0.2, 2 * self.rayVector,
                                             pg.Vector2((random() - 0.5) * 0.4, (random() - 0.5) * 0.4),
                                             self.origin)
        self.lighting = lighting
        self.targetPos = None

    def setAngle(self, angle):

        self.rayVector = pg.Vector2(math.cos(self.rotation), -math.sin(self.rotation))
        self.rotation = angle
        self.targetPos = None

        self.particleGen.setMaxVel(2 * self.rayVector)

    def move(self, position):
        self.origin = position
        self.particleGen.move(position)

    def rayCast(self, screen):

        if self.targetPos:
            if self.lighting:
                self.lightUp(screen)

            pg.draw.line(screen, self.color, self.origin, self.targetPos, self.laserWidth)

            return

        depth = 1

        nextPos = self.origin + self.rayVector * depth

        while 0 < nextPos.x < winWidth and 0 < nextPos.y < winHeight:
            pg.draw.line(screen, self.color, self.origin, nextPos, self.laserWidth)
            depth += 1

            nextPos = self.origin + self.rayVector * depth
            collision = Mirror.Mirror.checkCollision(nextPos)

            if collision[0] and depth > 5:
                obj = collision[1]
                collidedPos = self.origin + self.rayVector * (depth - 1)
                self.rotation %= 2 * pi
                if obj.interact(self, collidedPos):
                    self.targetPos = collidedPos
                    break
        else:
            self.targetPos = nextPos

    def lightUp(self, screen):

        if not GlobalVariables.lightupSimulation: return

        steps = 6

        offset = pg.Vector2((self.brightness * steps), (self.brightness * steps))

        dims = (math.fabs(self.targetPos.x - self.origin.x) + 2 * offset.x,
                math.fabs(self.targetPos.y - self.origin.y) + 2 * offset.y)

        startPoint = pg.Vector2(
            self.origin.x - min(self.origin.x, self.targetPos.x),
            self.origin.y - min(self.origin.y, self.targetPos.y)) + offset

        endPoint = pg.Vector2(
            self.targetPos.x - min(self.origin.x, self.targetPos.x),
            self.targetPos.y - min(self.origin.y, self.targetPos.y)) + offset

        center = (startPoint + endPoint) / 2

        for i in range(1, (self.brightness * steps), steps):
            surf = pg.surface.Surface(dims)
            Rectangle(
                center,
                self.rotation,
                i,
                (startPoint - endPoint).magnitude() + 10,
                (
                    self.brightness + math.floor(3 * (self.color.r / 255)),
                    self.brightness + math.floor(3 * (self.color.g / 255)),
                    self.brightness + math.floor(3 * (self.color.b / 255))
                )
            ).draw(surf)

            screen.blit(surf, (
                min(self.origin.x, self.targetPos.x) - offset.x,
                min(self.origin.y, self.targetPos.y) - offset.y),
                        special_flags=pg.BLEND_RGB_ADD)

        return

    def kill(self):
        self.particleGen.kill()
        del self
