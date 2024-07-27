from scripts.screens import *
from scripts.object_handler import ObjectHandler
from scripts.save_and_load import InstanceManager
import sys
import os


class Simulation:

    def __init__(self, width, height):
        self.width, self.height = width, height
        self.display = pg.display.set_mode((width, height))
        self.clock = pg.time.Clock()

        self.running = True
        self.object_handler = ObjectHandler(self)
        self.instance_manager = InstanceManager(self)

        self.current_save = None

        self.screens = {
            # 'test': Test(self),
            'build': Build(self),
            'simulation': Simulate(self),
            'options': Options(self),
            'saves': Saves(self)
        }

        self.__active_screen = 'build'

        self.load_instance(open('saves/last_save.txt').read())

    def save_instance(self, name):
        self.instance_manager.save_instance(self.object_handler.objects, name)

    def load_instance(self, name):

        self.object_handler.delete_all_objects()
        if not name:
            self.save_instance('save')
            self.load_instance('save')
            return
        self.object_handler.objects = self.instance_manager.load_instance(name)
        self.current_save = name

    @staticmethod
    def delete_instance(name):
        os.remove(f'saves/{name}.lpi')

    def clear_screen(self):
        self.active_screen.clear()

    def save(self):
        self.save_instance(self.current_save)

    def quit(self, *args):
        open('saves/last_save.txt', 'w').write(self.current_save)
        self.running = False

    def run(self):

        for s in self.screens.values():
            s.start()

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

    def set_active_screen(self, name):
        self.__active_screen = name

    def __getitem__(self, item):
        return self.screens[item]
