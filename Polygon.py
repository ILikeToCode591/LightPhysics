from GlobalVariables import *
from random import randint


class Rectangle:

    def __init__(self, position, rotation, width, length, color, children = tuple()):
        self.position = position
        self.rotation = rotation
        self.width = width
        self.length = length
        self.color = pg.Color(*color)

        self.angleVector = pg.Vector2(math.cos(self.rotation), -math.sin(self.rotation))
        self.normalVector = pg.Vector2(self.angleVector.y, -self.angleVector.x)
        self.halfLength = self.angleVector * self.length / 2
        self.halfWidth = self.normalVector * self.width / 2

        self.vertices = (
            (self.position - self.halfLength - self.halfWidth),
            (self.position - self.halfLength + self.halfWidth),
            (self.position + self.halfLength + self.halfWidth),
            (self.position + self.halfLength - self.halfWidth)
        )

        self.children = []
        self.children.extend(children)

        self.vibrating = False

        self.update()

    def draw(self, screen):

        if self.vibrating:
            randomness = pg.Vector2(randint(0, 3), randint(-1, 1))
            pg.draw.polygon(screen, self.color, tuple(randomness + vertex for vertex in self.vertices))
        else:
            pg.draw.polygon(screen, self.color, self.vertices)

    def update(self):

        self.rotation %= 2*pi

        self.angleVector = pg.Vector2(math.cos(self.rotation), -math.sin(self.rotation))
        self.normalVector = pg.Vector2(self.angleVector.y, -self.angleVector.x)
        self.halfLength = self.angleVector * self.length / 2
        self.halfWidth = self.normalVector * self.width / 2

        self.vertices = (
            (self.position - self.halfLength - self.halfWidth),
            (self.position - self.halfLength + self.halfWidth),
            (self.position + self.halfLength + self.halfWidth),
            (self.position + self.halfLength - self.halfWidth)
        )

        for child in self.children:
            child[0].move(self.position + child[2][0]*self.halfLength + child[2][1]*self.halfWidth)
            child[1](self.rotation)
            child[0].move(self.position + child[2][0] * self.halfLength + child[2][1] * self.halfWidth)
            child[1](self.rotation)

    def move(self, position):
        self.position = position
        self.update()

    def rotate(self, angle):
        self.rotation += angle
        self.update()

    def checkCollisions(self, point):
        count = 0
        index = 0
        while index < len(self.vertices):
            x1, y1 = self.vertices[index]
            x2, y2 = self.vertices[(index + 1) % len(self.vertices)]

            if (point.y < y1) != (point.y < y2) and point.x < x1 + ((point.y - y1) / (y2 - y1)) * (x2 - x1):
                count += 1
            index += 1

        if count % 2:
            return True