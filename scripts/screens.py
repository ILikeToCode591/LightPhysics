from config import *
from scripts.shapes import *
from random import randint
import os
from scripts.objects import *
from scripts.object_handler import ObjectHandler, WidgetHandler


class Screen:

    def __init__(self, sim, *flags):

        self.simulator = sim

        self.width, self.height = sim.width, sim.height
        self.event_handler = EventHandler()
        self.running = True

        self.event_handler.register(pg.QUIT, sim.quit)

        self.display = pg.Surface((self.width, self.height))
        self.light_scrn = pg.Surface((self.width, self.height), pg.SRCALPHA)
        self.shader_scrn = pg.Surface((self.width, self.height), pg.SRCALPHA)

    def clear(self):
        self.display.fill((0, 0, 0, 0))

    def start(self):
        pass

    def repeat(self):
        pass

    def event_loop(self):
        for event in pg.event.get():
            self.event_handler.broadcast(event)
        self.event_handler.repeat_event_broadcast()


class Simulate(Screen):
    def __init__(self, *args):

        super().__init__(*args)

        self.widget_handler = WidgetHandler(self)
        self.object_handler = self.simulator.object_handler
        self.shader = True
        self.shader_button = None

    def start(self):
        self.widget_handler.register_widget(
            Button(
                pg.Vector2((win_width - 40, win_height - 40)),
                60, 60,
                onclick=None,
                onrelease=self.build,
                icon='pause.png'
            )
        )
        self.shader_button = Button(
                pg.Vector2((win_width - 40, 40)),
                60, 60,
                onclick=None,
                onrelease=self.toggle_shaders,
                icon='bulb_lit.png'
            )

        self.widget_handler.register_widget(self.shader_button)

    def build(self):
        self.simulator.set_active_screen('build')

    def toggle_shaders(self):
        self.shader = not self.shader

        self.shader_button.set_image(icon = 'bulb_unlit.png' if not self.shader else 'bulb_lit.png')

    def repeat(self):
        self.display.fill(background)
        self.light_scrn.fill(transparent)
        self.shader_scrn.fill(transparent)

        for o in self.object_handler.objects:

            o.render(self.display, self.light_scrn, True)

            if self.shader:
                o.shader(self.shader_scrn)

        self.display.blit(self.shader_scrn, (0, 0))
        self.display.blit(self.light_scrn, (0, 0))
        self.widget_handler.render_widgets(self.display)


class Saves(Screen):

    def __init__(self, *args):
        super().__init__(*args)
        self.widget_handler = WidgetHandler(self)

        self.event_handler.register_key_event(pg.K_ESCAPE, self.options, repeat=False)

        self.saves = 0
        self.buttons = {}
        self.scroll = 0

        self.save_name = None
        self.save_button = None

    def start(self):
        self.load_saves()

    def load_saves(self):

        for f in os.listdir('saves'):
            if f.endswith('.lpi'):
                name = f.partition('.')[0]

                self.buttons[name] = (
                    Button(
                        pg.Vector2(
                            win_width//2 - button_s//2 - paddingh//2,
                            self.saves*(paddingv+button_s) + paddingv + button_s//2
                        ),
                        win_width - 3*paddingh - button_s, button_s,
                        onclick=lambda s = name : self.load_save(s),
                        name = name,
                        font_size=button_s-20
                    ), Button(
                        pg.Vector2(
                            win_width - paddingh - button_s//2,
                            self.saves*(paddingv+button_s) + paddingv + button_s//2
                        ),
                        button_s, button_s,
                        onclick=lambda s=name: self.buttn_del(s),
                        icon='trash.png'
                    )
                )

                self.saves+=1

                self.widget_handler.register_widget(self.buttons[name][0])
                self.widget_handler.register_widget(self.buttons[name][1])

        self.save_name = TextInput(
                pg.Vector2(win_width / 2, self.saves * (button_s + paddingv) + paddingv + button_s // 2),
                200, height=50, font_size=70, allow_period=False
            )

        self.save_name.activate()

        self.save_button = Button(
                pg.Vector2(win_width / 2 + 100 + 25, self.saves * (button_s + paddingv) + paddingv + button_s // 2),
                50, 50,
                onrelease=self.add_save,
                name='+',
                font_size=80
            )

        self.widget_handler.register_widget(self.save_name)
        self.widget_handler.register_widget(self.save_button)

    def load_save(self, name):
        self.simulator.load_instance(name)
        self.build()

    def add_save(self):
        name = self.save_name.string
        self.save_name.clear()

        if not name: return

        self.buttons[name] = (
            Button(
                pg.Vector2(
                    win_width // 2 - button_s // 2 - paddingh // 2,
                    self.saves * (paddingv + button_s) + paddingv + button_s // 2
                ),
                win_width - 3 * paddingh - button_s, button_s,
                onclick=lambda: self.load_save(name),
                name=name,
                font_size=button_s - 20
            ),
            Button(
                pg.Vector2(
                    win_width - paddingh - button_s // 2,
                    self.saves * (paddingv + button_s) + paddingv + button_s // 2
                ),
                button_s, button_s,
                onclick=lambda: self.buttn_del(name),
                icon='trash.png'
            )
        )

        self.widget_handler.register_widget(self.buttons[name][0])
        self.widget_handler.register_widget(self.buttons[name][1])
        self.saves += 1

        self.save_name.position.y += button_s+paddingv
        self.save_name.rect.center = self.save_name.position

        self.save_button.position.y += button_s + paddingv
        self.save_button.rect.center = self.save_button.position

        self.simulator.load_instance(name)
        self.build()

    def buttn_del(self, name):
        self.buttons[name][1].onrelease = lambda: self.delete(name)

    def delete(self, name):
        if self.saves == 1:
            return

        self.simulator.delete_instance(name)
        self.saves = 0

        self.event_handler.clear_all_events()
        self.buttons.clear()
        self.widget_handler.widgets.clear()
        self.event_handler.register_key_event(pg.K_ESCAPE, self.options, repeat=False)
        self.event_handler.register(pg.QUIT, self.simulator.quit)

        self.start()

        if name == self.simulator.current_save:
            self.simulator.load_instance(list(self.buttons.keys())[0])

    def build(self, *args):
        self.simulator.set_active_screen('build')

    def options(self, *args):
        self.simulator.set_active_screen('options')

    def repeat(self):
        self.display.fill(background)
        self.widget_handler.render_widgets(self.display)


class Options(Screen):

    def __init__(self, *args):
        super().__init__(*args)
        self.widget_handler = WidgetHandler(self)

    def start(self):
        self.widget_handler.register_widget(
            Button(pg.Vector2(win_width//2, win_height//2 - 55),
                   250, 100, self.build, None, name='BACK', font_size=80)
        )

        self.widget_handler.register_widget(
            Button(pg.Vector2(win_width // 2, win_height // 2 + 55),
                   250, 100, self.saves, None, name='SAVES', font_size=80)
        )
        self.widget_handler.register_widget(
            Button(pg.Vector2(win_width // 2 - 125 - 35, win_height // 2 + 55),
                   60, 60, self.simulator.save, None, icon='floppy.png', font_size=80)
        )

    def build(self):
        self.simulator.set_active_screen('build')

    def controls(self):
        pass

    def saves(self):
        self.simulator.set_active_screen('saves')

    def repeat(self):
        self.display.fill(background)
        self.widget_handler.render_widgets(self.display)


class Build(Screen):

    def __init__(self, *args):
        super().__init__(*args)
        self.widget_handler = WidgetHandler(self)
        self.object_handler = self.simulator.object_handler

        self.event_handler.register_key_event(pg.K_ESCAPE, self.open_options, repeat=False)
        self.event_handler.register_key_event(pg.K_DELETE, self.object_handler.delete_object, repeat=False)

        self.in_mode = False

        self.modes = {
            pg.K_t: [
                {
                    pg.MOUSEBUTTONDOWN: ('n', self.object_handler.start_moving),
                    pg.MOUSEBUTTONUP: ('n', self.object_handler.stop_moving),
                    pg.MOUSEMOTION: ('n', self.object_handler.move_object),
                    pg.K_RIGHT : ('k', lambda *e: self.object_handler.rotate_object(1)),
                    pg.K_LEFT : ('k', lambda *e: self.object_handler.rotate_object(-1)),
                    pg.K_UP: ('k', lambda *e: self.object_handler.resize_object(1)),
                    pg.K_DOWN: ('k', lambda *e: self.object_handler.resize_object(-1))
                },
                self.event_handler.register_temp_event_slot()],
            pg.K_s: [{
                pg.MOUSEBUTTONDOWN: ('n', lambda *e: self.object_handler.select_object(self.modes[pg.K_c][1]))
            }, self.event_handler.register_temp_event_slot()],
            pg.K_c: [None, self.event_handler.register_temp_event_slot()]
        }

    def start(self):
        for key in list(self.modes.keys()):
            self.event_handler.register_key_event(key,
                                                  lambda *args, k=key: self.enter_mode(k),
                                                  lambda *args, k=key: self.leave_mode(k),
                                                  False)
        for key in list(self.modes.keys())[:-1]:
            for k, v in self.modes[key][0].items():
                if v[0] == 'k':
                    self.event_handler.register_temp_key_event(self.modes[key][1], k, v[1])
                elif v[0] == 'n':
                    self.event_handler.register_temp_event(self.modes[key][1], k, v[1])

        self.object_handler.register_class(Pointer)
        self.object_handler.register_class(PolyMirror)
        self.object_handler.register_class(PlaneMirror)

        self.widget_handler.register_widget(
            Button(
                pg.Vector2((win_width-40, win_height-40)),
                60, 60,
                onclick=None,
                onrelease=self.simulate,
                icon = 'play.png'
            )
        )

        for t, v in self.object_handler.texts:
            self.widget_handler.register_widget(t)
            self.widget_handler.widgets.remove(t)

        self.object_handler.update_object_info()

    def open_options(self, *args):
        if self.in_mode:
            return
        self.simulator.object_handler.reset = False
        self.simulator.set_active_screen('options')

    def simulate(self, *args):
        if self.in_mode:
            return
        self.simulator.object_handler.reset = False
        self.simulator.set_active_screen('simulation')

    def enter_mode(self, key):
        self.in_mode = True
        self.event_handler.activate_temp_event(self.modes[key][1])

        if key == pg.K_c and self.object_handler.selected_object:
            self.object_handler.selected_object.custom_frame.active = True
            self.object_handler.reset_instruments()

    def leave_mode(self, key):
        self.in_mode = False
        self.event_handler.deactivate_temp_event(self.modes[key][1])

        if key == pg.K_c and self.object_handler.selected_object:
            self.object_handler.selected_object.custom_frame.active = False

    def repeat(self):
        self.display.fill(background)
        for o in self.object_handler.objects:
            if o == self.object_handler.selected_object:
                o.render_mask(self.display)

            o.render(self.display, self.light_scrn, False)

        self.object_handler.render_object_info(self.display)
        self.widget_handler.render_widgets(self.display)


# class Test(Screen):
#     def __init__(self, *args):
#         super().__init__(*args)
#         self.sim = False
#         self.object_handler = self.simulator.object_handler
#
#     def start(self):
#         n = 20
#         randomness = 5
#         radius = 100
#         # pointers = [Pointer(pg.Vector2(randint(100, win_width-100), randint(100, win_height-100)), 0, pg.Color(*(randint(130, 255) for i in range(3))), 1) for i in range(5)]
#         # mirror = PolyMirror(pg.Vector2(300, 300), 0, [
#         #     pg.Vector2(radius + randint(-randomness, randomness), 0).rotate(i*(360/n)) for i in range(n)
#         # ])
#         mirror = PlaneMirror(pg.Vector2(500, 300), 45, 40)
#         pointers = [
#             Pointer(pg.Vector2(100, 100), 30, pg.Color(255, 0, 0), 1),
#             Pointer(pg.Vector2(100, 200), 0, pg.Color(0, 255, 0), 1),
#             Pointer(pg.Vector2(100, 300), -30, pg.Color(0, 0, 255), 1)
#         ]
#         for po in pointers:
#             self.object_handler.register_object(po)
#             self.event_handler.register_key_event(pg.K_RIGHT, lambda *args, p=po: p.rotate(1))
#             self.event_handler.register_key_event(pg.K_LEFT, lambda *args, p=po: p.rotate(-1))
#             self.event_handler.register_key_event(pg.K_UP, lambda *args, p=po: p.increase_size())
#             self.event_handler.register_key_event(pg.K_DOWN, lambda *args, p=po: p.decrease_size())
#             self.event_handler.register(pg.MOUSEBUTTONDOWN, lambda e, p=po: p.raycast() or self.toggle_sim())
#             self.event_handler.register_key_event(pg.K_d, lambda *args, p=po: p.displace(pg.Vector2(5, 0)))
#             self.event_handler.register_key_event(pg.K_w, lambda *args, p=po: p.displace(pg.Vector2(0, -5)))
#             self.event_handler.register_key_event(pg.K_a, lambda *args, p=po: p.displace(pg.Vector2(-5, 0)))
#             self.event_handler.register_key_event(pg.K_s, lambda *args, p=po: p.displace(pg.Vector2(0, 5)))
#
#         self.object_handler.register_object(mirror)
#         self.event_handler.register_key_event(pg.K_RIGHT, lambda *args, p=po: p.rotate(1))
#         self.event_handler.register_key_event(pg.K_LEFT, lambda *args, p=po: p.rotate(-1))
#         self.event_handler.register_key_event(pg.K_UP, lambda *args, p=po: p.increase_size())
#         self.event_handler.register_key_event(pg.K_DOWN, lambda *args, p=po: p.decrease_size())
#         self.event_handler.register_key_event(pg.K_d, lambda *args, p=po: p.displace(pg.Vector2(5, 0)))
#         self.event_handler.register_key_event(pg.K_w, lambda *args, p=po: p.displace(pg.Vector2(0, -5)))
#         self.event_handler.register_key_event(pg.K_a, lambda *args, p=po: p.displace(pg.Vector2(-5, 0)))
#         self.event_handler.register_key_event(pg.K_s, lambda *args, p=po: p.displace(pg.Vector2(0, 5)))
#
#     def toggle_sim(self):
#         self.sim = not self.sim
#
#     def repeat(self):
#         self.display.fill(background)
#         self.light_scrn.fill((0, 0, 0, 0))
#         self.shader_scrn.fill((0, 0, 0, 0))
#         self.draw_objects()
#
#     def draw_objects(self):
#         for obj in self.object_handler.objects:
#             obj.render(self.display, self.light_scrn, self.sim)
#             if self.sim:
#                 # obj.shader(self.shader_scrn)
#                 pass
#         self.display.blit(self.shader_scrn, (0, 0))
#         self.display.blit(self.light_scrn, (0, 0))
