from collections import defaultdict

from config import *


class EventHandler:

    def __init__(self):

        self.events = defaultdict(list)
        self.s_key_events = defaultdict(list)
        self.r_key_events = defaultdict(list)
        self.t_key_events = dict()

        self.t_events = dict()
        self.active_t_events = []

        self.pressed_keys = set()

    def register(self, event, function):
        self.events[event].append(function)

    def register_key_event(self, key : int, function_d, function_u=None, repeat=True):
        """

        :param key: which key pressed (keycode)
        :param function_d: what to be done if the key is pressed : function
        :param function_u: what to be done if the key is lifted : None/function
        :param repeat: if the function is repeating or not : bool
        :return: None
        """
        if repeat:
            self.r_key_events[key].append([function_d, function_u])
            return

        self.s_key_events[key].append([function_d, function_u])

    def clear_all_events(self):
        self.events = defaultdict(list)
        self.s_key_events = defaultdict(list)
        self.r_key_events = defaultdict(list)
        self.t_key_events = dict()

        self.t_events = dict()
        self.active_t_events = []

    def broadcast(self, event):
        for funct in self.events.get(event.type, []):
            funct(event)

        for key in self.active_t_events:
            for funct in self.t_events[key].get(event.type, []):
                funct(event)

            if event.type == pg.KEYDOWN:
                for f_grp in self.s_key_events.get(event.key, []):
                    if not f_grp[0]:
                        f_grp[1](event)

            if event.type == pg.KEYUP:
                for f_grp in self.t_key_events[key].get(event.key, []):
                    if f_grp[2]:
                        f_grp[2](event)

        if event.type == pg.KEYDOWN:
            self.pressed_keys.add(event.key)

            for f_grp in self.s_key_events.get(event.key, []):
                f_grp[0](event)

        if event.type == pg.KEYUP:
            if event.key not in self.pressed_keys:
                return
            self.pressed_keys.remove(event.key)
            for f_grp in self.s_key_events.get(event.key, []):
                if f_grp[1]:
                    f_grp[1](event)
            for f_grp in self.r_key_events.get(event.key, []):
                if f_grp[1]:
                    f_grp[1](event)

    def repeat_event_broadcast(self):
        for key in self.pressed_keys:

            for f_grp in self.r_key_events.get(key, []):
                for f in f_grp:
                    if f is not None:
                        f(key)
            for k in self.active_t_events:
                for f_grp in self.t_key_events[k].get(key, [[False]]):
                    if f_grp[0]:
                        for f in f_grp[1:]:
                            if f is not None:
                                f(key)

    def register_temp_event_slot(self):
        key = get_unique_key()
        self.t_events[key] = defaultdict(list)
        self.t_key_events[key] = defaultdict(list)
        return key

    def register_temp_event(self, key, event, function):
        self.t_events[key][event].append(function)

    def clear_all_temp_events(self, key):
        self.t_events[key] = defaultdict(list)
        self.t_key_events[key] = defaultdict(list)

    def register_temp_key_event(self, key, keypress: int, function_d, function_u=None, repeat=True):
        """

        :param key: temp event key
        :param keypress: which key is pressed (keycode)
        :param function_d: what to be done if the key is pressed : function
        :param function_u: what to be done if the key is lifted : None/function
        :param repeat: if the function is repeating or not : bool
        :return: None
        """

        if repeat:
            self.t_key_events[key][keypress].append([True, function_d, function_u])
            return

        self.t_key_events[key][keypress].append([False, function_d, function_u])

    def activate_temp_event(self, key):
        self.active_t_events.append(key)

    def deactivate_temp_event(self, key):
        self.active_t_events.remove(key)

