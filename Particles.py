import GlobalVariables
from GlobalVariables import *
from random import random, randint

class ParticleGenerator:

    allInstances = []
    maxParticleAmount = 1000

    def __init__(self, color, maxRadius, density, maxVelocity, acceleration, origin):
        self.maxRadius = maxRadius
        self.maxVelocity = maxVelocity
        self.acceleration = acceleration
        self.density = density
        self.origin = origin
        self.color = color

        self.particles = []

        ParticleGenerator.allInstances.append(self)

    def generateParticles(self):
        if random() <= self.density and len(self.particles) < ParticleGenerator.maxParticleAmount:
            newParticle = Particle(self.color, randint(1, self.maxRadius)*10, self.acceleration, self.maxVelocity * randint(2, 10)/10, self.origin)
            self.particles.append(newParticle)

    def draw(self, screen, draw):
        if draw:
            self.generateParticles()
            for particle in self.particles:
                particle.update(screen)

                if particle.lifetime < 0:
                    self.particles.remove(particle)
                    del particle

    def move(self, position):
        self.origin = position

    def setMaxVel(self, velocity):
        self.maxVelocity = velocity

    def kill(self):
        ParticleGenerator.allInstances.remove(self)
        del self

    @staticmethod
    def drawInstances(screen, draw):
        for gen in ParticleGenerator.allInstances:
            gen.draw(screen , draw)


class Particle:

    def __init__(self, color, lifetime, acceleration, velocity, position):
        self.color = color
        self.lifetime = lifetime
        self.acceleration = acceleration
        self.velocity = velocity
        self.position = position.copy()

    def update(self, screen):
        self.velocity += self.acceleration
        self.position += self.velocity

        if GlobalVariables.lightupSimulation:
            for r in range(2, self.lifetime-5):
                surf = pg.surface.Surface((2*r, 2*r))
                pg.draw.circle(surf, (1 + math.floor(3 * (self.color.r/255)), 1+ math.floor(3 * (self.color.g/255)), 1+ math.floor(3 * (self.color.b/255))), (r,r), r)

                screen.blit(surf, self.position - pg.Vector2(r, r), special_flags=pg.BLEND_RGB_ADD)

        pg.draw.circle(screen, self.color, self.position, self.lifetime/10)
        self.lifetime -= 1