from scripts.screens import *
import sys


class Simulation:

    def __init__(self, width, height):
        self.width, self.height = width, height
        self.display = pg.display.set_mode((width, height))
        self.clock = pg.time.Clock()

        self.running = True

        self.screens = {
            'test': Test(self),
            'build': Build(self),
            'simulation': Simulate(self)
        }

        self.__active_screen = 'build'

    def clear_screen(self):
        self.active_screen.clear()

    def quit(self, *args):
        self.running = False

    def run(self):
        self.active_screen.start()

        while self.running:
            self.display.fill(background)

            self.active_screen.event_loop()

            self.active_screen.repeat()

            self.display.blit(self.active_screen.display, (0, 0))

            pg.display.flip()
            self.clock.tick(60)

        pg.quit()
        sys.exit()

    @property
    def active_screen(self) -> Screen:
        return self.screens[self.__active_screen]

    def set_active_screen(self, name, start = False):
        self.__active_screen = name

        if start:
            self.active_screen.start()

    def __getitem__(self, item):
        return self.screens[item]
