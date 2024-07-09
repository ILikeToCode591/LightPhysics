from config import *
from scripts.gui import *
from scripts.objects import Interactable, Instrument


class ObjectHandler:

    def __init__(self, screen):
        self.registered_classes = []
        self.objects = []
        self.screen = screen

        self.selected_object = None
        self.moving_object = False

        self.texts = [
            (Text('0', white, (10, 10), 35, 'tl'),
             lambda : 'posx:  ' + str(self.selected_object.position.x)[:5]),
            (Text('0', white, (90, 10), 35, 'tl'),
             lambda: 'posy:  ' + str(self.selected_object.position.y)[:5]),
            (Text('0', white, (170, 10), 35, 'tl'),
             lambda: 'rotn:  ' + str(self.selected_object.rotation)[:5])
        ]

        self.widgets : list[Widget] = []

    def register_class(self, cl : Interactable | Instrument):
        n = len(self.registered_classes)
        self.widgets.append(Button(pg.Vector2(
            widget_button_padding*(n+1) + widget_button_width*(n+0.5),
            win_height - widget_button_height/2 - widget_button_padding),

            widget_button_width, widget_button_height,

            lambda : self.register_object(cl.create_object()),

            icon=cl.icon
            )
        )
        self.registered_classes.append(cl)

    def render_widgets(self, screen):
        for b in self.widgets:
            b.render(screen)

        if self.selected_object and self.selected_object.custom_frame.active:
            self.selected_object.custom_frame.render(screen)

        if self.selected_object:
            for text in self.texts:
                text[0].update_text(text[1]())
                screen.blit(text[0].image, text[0].rect)

    def register_widget_triggers(self):
        for w in self.widgets:
            for t in w.triggers:
                for grp in w.triggers[t]:
                    if grp[0] == 'n':
                        self.screen.event_handler.register(t, grp[1])
                    elif type == 'k':
                        self.screen.event_handler.register_key_event(*tuple(grp[1:]))

    def register_object(self, obj):
        self.objects.append(obj)

    def select_object(self, key, *args):
        for o in self.objects[::-1]:
            if o.check_selection(pg.Vector2(pg.mouse.get_pos())):
                if self.selected_object == o:
                    self.deselect_object(key)
                    break
                self.selected_object = o
                for e in self.selected_object.custom_frame.registered_events:
                    self.screen.event_handler.register_temp_event(key,
                                                                  e,
                                                                  self.selected_object.custom_frame.broadcast)
                break
        else:
            self.deselect_object(key)

    def deselect_object(self, key):
        self.selected_object = None
        self.screen.event_handler.clear_all_temp_events(key)

    def start_moving(self, event):
        if event.button == pg.BUTTON_LEFT and self.selected_object:
            self.moving_object = True
            self.selected_object.move_to(pg.Vector2(pg.mouse.get_pos()))

    def move_object(self, event):
        if self.selected_object and self.moving_object:
            self.selected_object.move_to(pg.Vector2(pg.mouse.get_pos()))

    def stop_moving(self, event):
        if event.button == pg.BUTTON_LEFT and self.selected_object:
            self.moving_object = False

    def rotate_object(self, angle):
        if self.selected_object:
            self.selected_object.rotate(angle)

    def resize_object(self, inc):
        if self.selected_object:
            self.selected_object.increase_size() if inc > 0 else self.selected_object.decrease_size()

