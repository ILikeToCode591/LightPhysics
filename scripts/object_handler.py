from config import *
from scripts.gui import *
from scripts.objects import Objects, Interactives, Interactable, Pointer


class WidgetHandler:

    def __init__(self, screen):
        self.widgets = []
        self.screen = screen

    def render_widgets(self, screen):
        for b in self.widgets:
            b.render(screen)

    def register_widget(self, w):
        self.widgets.append(w)

        for t in w.triggers:
            for grp in w.triggers[t]:
                if grp[0] == 'n':
                    self.screen.event_handler.register(t, grp[1])
                elif grp[0] == 'k':
                    self.screen.event_handler.register_key_event(t, *tuple(grp[1:]))


class ObjectHandler:
    def __init__(self, sim):
        self.registered_classes = []
        self.objects = []
        self.sim = sim

        self.reset = False

        self.selected_object = None
        self.moving_object = False

        self.texts = [
            (
                TextInput(pg.Vector2(30, 30), 40, allow_letters=False, on_entry=lambda s: self.set_object_pos('x', float(s)), label = 'Pos x'),
                lambda : self.selected_object.position.x
            ),
            (
                TextInput(pg.Vector2(80, 30), 40, allow_letters=False, on_entry=lambda s: self.set_object_pos('y', float(s)), label = 'Pos y'),
                lambda: self.selected_object.position.y
            ),
            (
                TextInput(pg.Vector2(130, 30), 40, allow_letters=False, on_entry=lambda s: self.set_rotation(float(s)), label='Rot'),
                lambda: self.selected_object.rotation
            )
        ]

    def register_class(self, cl: Objects):

        build_screen = self.sim.screens['build']

        n = len(self.registered_classes)

        build_screen.widget_handler.register_widget(Button(pg.Vector2(
            widget_button_padding*(n+1) + widget_button_width*(n+0.5),
            win_height - widget_button_height/2 - widget_button_padding),

            widget_button_width, widget_button_height,

            lambda : self.register_object(cl.create_object()),

            icon=cl.icon
            )
        )
        self.registered_classes.append(cl)

    def render_object_info(self, screen):
        if self.selected_object:
            for text in self.texts:
                text[0].render(screen)

        if self.selected_object and self.selected_object.custom_frame.active:
            self.selected_object.custom_frame.render(screen)

    def update_object_info(self):
        if self.selected_object:
            for text in self.texts:
                text[0].update_text(str(text[1]()))

    def register_object(self, obj):
        if isinstance(obj, Interactable):
            self.reset_instruments()

        self.objects.append(obj)

    def delete_all_objects(self):
        for o in self.objects:
            if isinstance(o, Interactives):
                Interactable.all_instances.remove(o)
        self.reset_instruments()
        self.objects.clear()
        self.selected_object=None

    def delete_object(self, event):
        obj = self.selected_object
        self.objects.remove(obj)
        if isinstance(obj, Interactives):
            Interactable.all_instances.remove(obj)
        self.reset_instruments()
        self.selected_object = None

    def reset_instruments(self):
        if self.reset: return
        for i in self.objects:
            if isinstance(i, Pointer):
                i.reset()

        self.reset = True

    def select_object(self, key, *args):
        build_screen = self.sim.screens['build']

        for o in self.objects[::-1]:
            if o.check_selection(pg.Vector2(pg.mouse.get_pos())):
                if self.selected_object == o:
                    self.deselect_object(key)
                    break
                self.selected_object = o
                for e in self.selected_object.custom_frame.registered_events:
                    build_screen.event_handler.register_temp_event(key,
                                                                  e,
                                                                  self.selected_object.custom_frame.broadcast)

                for t, v in self.texts:
                    t.activate()
                self.update_object_info()
                break
        else:
            self.deselect_object(key)

    def deselect_object(self, key):
        self.selected_object = None
        self.sim.screens['build'].event_handler.clear_all_temp_events(key)

        for t, v in self.texts:
            t.deactivate()

    def start_moving(self, event):
        if event.button == pg.BUTTON_LEFT and self.selected_object:
            self.moving_object = True
            self.selected_object.move_to(pg.Vector2(pg.mouse.get_pos()))
            self.reset_instruments()

    def set_object_pos(self, axis, pos):
        if self.selected_object:
            position = pg.Vector2(0, 0)
            if axis == 'x':
                position.x = pos
                position.y = self.selected_object.position.y
            else:
                position.y = pos
                position.x = self.selected_object.position.x

            self.selected_object.move_to(position)
            self.reset_instruments()

    def move_object(self, event):
        if self.selected_object and self.moving_object:
            self.selected_object.move_to(pg.Vector2(pg.mouse.get_pos()))
            self.reset_instruments()
            self.update_object_info()

    def stop_moving(self, event):
        if event.button == pg.BUTTON_LEFT and self.selected_object:
            self.moving_object = False

    def set_rotation(self, angle):
        if self.selected_object:
            self.selected_object.rotate(angle - self.selected_object.rotation)
            self.reset_instruments()

    def rotate_object(self, angle):
        if self.selected_object:
            self.selected_object.rotate(angle)
            self.reset_instruments()
            self.update_object_info()

    def resize_object(self, inc):
        if self.selected_object:
            self.selected_object.increase_size() if inc > 0 else self.selected_object.decrease_size()
            self.reset_instruments()

