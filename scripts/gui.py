from config import *
from collections import defaultdict
from scripts.event_handler import EventHandler


class Widget:

    def __init__(self, position):
        self.position = position
        self.image = None
        self.rect = None

        self.pre_render = False

        self.triggers = defaultdict(list)

    def render(self, screen: pg.surface.Surface):
        if self.pre_render:
            self.render_subclass(screen)
        screen.blit(self.image, self.rect)
        if not self.pre_render:
            self.render_subclass(screen)

    def render_subclass(self, screen):
        pass


class Text(Widget):

    def __init__(self, text, color, position, size, anchor = 'c'):
        super().__init__(position)

        self.font = pg.font.Font('assets/fonts/game_over.ttf', size)
        self.text = text
        self.color = color
        self.image = self.font.render(text, True, color)
        self.rect = self.image.get_rect()

        self.anchor = anchor

        self.anchor_self(position)

    def update_text(self, text=None, color=None):
        self.text = text if text is not None else self.text
        self.color = color if color else self.color

        self.image = self.font.render(self.text, True, self.color)
        self.rect = self.image.get_rect()
        self.anchor_self(self.position)

    def anchor_self(self, position):
        self.position = position

        if self.anchor == 'c':
            self.rect.center = position
        elif self.anchor == 'tl':
            self.rect.topleft = position
        elif self.anchor == 'tr':
            self.rect.topright = position
        elif self.anchor == 'bl':
            self.rect.bottomleft = position


class TextInput(Widget):
    def __init__(self, position, width, height = 20, font_size = 35, on_entry = None, allow_letters = True, allow_numbers = True, allow_period = True, label = None, label_color = white):
        super().__init__(position)

        self.width = width
        self.height = height

        self.active = False

        self.string = ''
        self.selected = False

        self.font_size = font_size
        self.on_entry = on_entry
        self.period = allow_period
        self.letter = allow_letters
        self.number = allow_numbers

        self.t = 0

        self.background = NineSliced(*text_box_img)

        self.image = self.background.create_image(width, height)
        self.rect = self.image.get_rect()

        self.rect.center = self.position
        self.label = None
        if label:
            self.label = Text(label, label_color, self.rect.topleft, 35, 'bl')

        self.text = Text(self.string, black, pg.Vector2(5, 0), self.font_size, anchor='tl')

        self.triggers[pg.KEYDOWN].append(('n', self.add_to_string))
        self.triggers[pg.MOUSEBUTTONDOWN].append(('n', self.select))
        self.triggers[pg.K_RETURN].append(('k', self.enter, None, False))
        self.triggers[pg.K_BACKSPACE].append(('k', self.backspace, None, True))

    def add_to_string(self, event):
        if not self.selected: return
        str = pg.key.name(event.key)
        if len(str) == 1 and ((str.isalpha() and self.letter) or
                              (str.isdigit() and self.number) or
                              str in '_' or
                              (str in '.' and self.period)):
            self.string = self.string+str
        self.text.update_text(text = self.string)

        self.create_image()

    def clear(self):
        self.string = ''
        self.text.update_text(text=self.string)

        self.create_image()

    def update_text(self, val):
        self.string = val
        self.text.update_text(text = self.string)

        self.create_image()

    def select(self, event):
        if not self.active:
            return

        if not self.rect.collidepoint(*pg.mouse.get_pos()):
            self.selected = False
        else:
            self.selected = True

        self.create_image()

    def backspace(self, *args):
        if not self.selected: return
        if self.string:
            self.string = self.string[:-1]

        self.text.update_text(text=self.string)

        self.create_image()

    def deactivate(self):
        self.active = False
        self.selected = False

    def activate(self):
        self.active = True

    def enter(self, *args):
        if self.on_entry and self.selected:
            self.on_entry(self.string)
        self.selected = False

    def create_image(self):
        self.image = self.background.create_image(self.width, self.height)

        if self.text.rect.width > self.width:
            self.text.anchor = 'tr'
            self.text.anchor_self(pg.Vector2(self.width-5, 0))
        else:
            self.text.anchor = 'tl'
            self.text.anchor_self(pg.Vector2(5, 0))

        self.text.render(self.image)

    def render_subclass(self, screen):

        if self.label:
            self.label.render(screen)

        if not self.selected: return

        self.t += 0.02
        if self.t == 2:
            self.t = 0
        if int(self.t) % 2:
            pg.draw.rect(screen, black, (
                *tuple(pg.Vector2(self.rect.topleft) + pg.Vector2(self.text.rect.topright)), 4, self.text.rect.height
            ))


class Button(Widget):
    def __init__(self, position, width, height, onclick = None, onrelease = None,  name: str = None, icon: str = None,
                 mouse_button: int = pg.BUTTON_LEFT, font_size = 30):

        super().__init__(position)

        self.width = width
        self.height = height

        self.button_slices = NineSliced(*button_img)
        self.button_active_slices = NineSliced(*button_p_img)

        self.font_size = font_size

        self.clicked = False
        self.onclick = onclick
        self.onrelease = onrelease

        self.mouse_button = mouse_button

        self.name_and_icon = name,icon

        self.set_image(*self.name_and_icon)

        self.triggers[pg.MOUSEBUTTONDOWN].append(('n', self.click))
        self.triggers[pg.MOUSEBUTTONUP].append(('n', self.release))

    def click(self, event):
        if event.button == self.mouse_button and self.rect.collidepoint(*pg.mouse.get_pos()):
            self.clicked = True
            if self.onclick:
                self.onclick()
            self.set_image(*self.name_and_icon)

    def set_image(self, name= None, icon = None):
        self.image = (self.button_slices if not self.clicked else self.button_active_slices).create_image(
            self.width, self.height
        )
        self.rect = self.image.get_rect()

        if name:
            Text(name, black, pg.Vector2(self.width, self.height) / 2, self.font_size).render(self.image)
        if icon:
            img = pg.image.load(get_asset(('texture', 'icon'), *tuple(icon.split('.'))))
            rect = img.get_rect()

            rect.center = pg.Vector2(self.width, self.height) / 2
            self.image.blit(img, rect)

        self.rect.center = self.position

    def release(self, event):
        if self.clicked and event.button == self.mouse_button and self.rect.collidepoint(*pg.mouse.get_pos()):
            self.clicked = False
            if self.onrelease:
                self.onrelease()
            self.set_image(*self.name_and_icon)

    def __str__(self):
        return f'Button({self.name_and_icon[0]})'


class ImageButton(Button):

    def __init__(self, position, width, height, onclick, onrelease = None, image: str = None, mouse_button: int = pg.BUTTON_LEFT):
        super().__init__(position, 100, 100, onclick, onrelease, name='0', mouse_button=mouse_button)
        self.image = pg.transform.scale(pg.image.load(get_asset(('texture', 'image'), *tuple(image.split('.')))),
                                        (width, height))
        self.rect = self.image.get_rect()
        self.rect.center = position


class ColorPicker(Widget):

    def __init__(self, position, length, funct, color=pg.Color(255, 0, 0), vertical=True):
        super().__init__(position)

        bg_color = pg.Color(150, 150, 150)
        corner_rad = 10

        self.p = color.hsla[0] / 360
        self.color = color
        self.vertical = vertical
        self.length = length
        self.position = position

        self.funct = funct

        anc = (0, 1) if vertical else (1, 0)

        self.image = pg.Surface((length * anc[0] + 50, length * anc[1] + 50), flags=pg.SRCALPHA)

        self.image.fill(bg_color)
        w, h = self.image.get_size()
        for p in ((0, 0), (1, 0), (1, 1), (0, 1)):
            pos = pg.Vector2(p[0]*w, p[1]*h)
            pg.draw.circle(self.image, pg.Color(0, 0, 0, 0), pos, corner_rad)
            pg.draw.circle(self.image, bg_color, pos + pg.Vector2(
                ((-1 if p[0] else 1)*corner_rad, (-1 if p[1] else 1)*corner_rad)), corner_rad)
            pg.draw.circle(self.image, bg_color.lerp(black, 0.5), pos + pg.Vector2(
                ((-1 if p[0] else 1) * corner_rad, (-1 if p[1] else 1) * corner_rad)), 3)

        for i in range(length):
            pg.draw.circle(self.image, black, (25 + i * anc[0], 25 + i * anc[1]), 13)
        for i in range(length):
            col = pg.Color(0, 0, 0)
            col.hsla = (int(360 * i / length), 100, 50, 100)
            pg.draw.circle(self.image, col, (25 + i * anc[0], 25 + i * anc[1]), 10)

        self.rect = self.image.get_rect()
        self.rect.center = position

        self.tracking = False

        self.triggers[pg.MOUSEBUTTONDOWN].append(('n', self.start_track))
        self.triggers[pg.MOUSEBUTTONUP].append(('n', self.stop_track))
        self.triggers[pg.MOUSEMOTION].append(('n', self.track))

    def start_track(self, event):
        if event.button == pg.BUTTON_LEFT and self.rect.collidepoint(*pg.mouse.get_pos()):
            self.tracking = True

            pos = pg.Vector2(pg.mouse.get_pos())

            if self.vertical:
                self.p = pos.y - (self.position.y - self.length // 2)
            else:
                self.p = pos.x - (self.position.x - self.length // 2)

            self.p /= self.length
            self.p = max(0, min(self.p, 1))

            self.color.hsla = (int(self.p * 360), 100, 50, 100)

            self.funct(self.color)

    def stop_track(self, event):
        if event.button == pg.BUTTON_LEFT and self.tracking:
            self.tracking = False

    def track(self, event):
        if not self.tracking:
            return

        pos = pg.Vector2(pg.mouse.get_pos())

        if self.vertical:
            self.p = pos.y - (self.position.y - self.length // 2)
        else:
            self.p = pos.x - (self.position.x - self.length // 2)

        self.p /= self.length
        self.p = max(0, min(self.p, 1))

        self.color.hsla = (int(self.p * 360), 100, 50, 100)

        self.funct(self.color)

    def render_subclass(self, screen):
        if self.tracking:
            mouse = pg.mouse.get_pos()
            if self.vertical:
                pos = (self.position.x, max(self.position.y - self.length // 2,
                                            min(mouse[1], self.position.y + self.length // 2)
                                            ))
            else:
                pos = (max(self.position.x - self.length // 2,
                           min(mouse[0], self.position.x + self.length // 2)
                           ), self.position.y)

            pg.draw.circle(screen, self.color, pos, 15)
            pg.draw.circle(screen, black, pos, 15, 3)


class Image(Widget):
    def __init__(self, position, width, height, name):
        super().__init__(position)
        self.image = pg.transform.scale(pg.image.load(get_asset(('texture', 'image'), *tuple(name.split('.')))),
                                        (width, height))
        self.rect = self.image.get_rect()
        self.rect.center = self.position


class NineSliced:
    widthError = ValueError('width is too low')
    heightError = ValueError('length is too low')

    def __init__(self, base_image, slices: tuple[int, int, int, int]):

        self.base_image = pg.image.load(base_image)
        self.left, self.right, self.top, self.bottom = self.slices = slices
        self.centre = (
        self.left, self.top, self.base_image.get_width() - self.right, self.base_image.get_height() - self.bottom)
        self.parts = {}

        self.create_parts()

    def create_parts(self):

        horizontals = (0, self.left, self.centre[2], self.base_image.get_width())
        verticals = (0, self.top, self.centre[3], self.base_image.get_height())
        self.parts.clear()

        for v in range(len(verticals) - 1):
            for h in range(len(horizontals) - 1):
                surface = pg.surface.Surface((horizontals[h + 1] - horizontals[h], verticals[v + 1] - verticals[v]),
                                             pg.SRCALPHA)

                surface.blit(self.base_image, (0, 0),
                             (horizontals[h], verticals[v], horizontals[h + 1], verticals[v + 1]))

                self.parts[len(self.parts)] = surface.copy()

    def create_image(self, width, height, scale=1) -> pg.surface.Surface:

        if width < self.base_image.get_width():
            raise self.widthError
        if height < self.base_image.get_height():
            raise self.heightError

        horizontal_resize = width - (self.left + self.right) * scale
        vertical_resize = height - (self.top + self.bottom) * scale

        horizontals = (0, self.left * scale, width - self.right * scale, width)
        verticals = (0, self.top * scale, height - self.bottom * scale, height)

        image = pg.surface.Surface((width, height), pg.SRCALPHA)
        part = 0

        for v in range(len(verticals) - 1):
            for h in range(len(horizontals) - 1):
                image.blit(pg.transform.scale(self.parts[part], (
                    horizontal_resize if h % 2 else (self.parts[part].get_width()) * scale,
                    vertical_resize if v % 2 else (self.parts[part].get_height()) * scale)
                    ), (horizontals[h], verticals[v], horizontals[h + 1], verticals[v + 1])
                )
                part += 1

        return image


class Frame:

    def __init__(self, width, height, position):
        self.width = width
        self.height = height
        self.position = position

        self.surface = pg.Surface((width, height))
        self.surface.fill(background.lerp(black, 0.5))

        self.event_handler = EventHandler()
        self.widgets = []
        self.registered_events = set()

        self.active = False

    def add_widget(self, w):
        for t in w.triggers:
            for grp in w.triggers[t]:
                if grp[0] == 'n':
                    self.event_handler.register(t, grp[1])
                    self.registered_events.add(t)
                elif grp[0] == 'k':
                    self.event_handler.register_key_event(t, *tuple(grp[1:]))
                    self.registered_events.add(pg.KEYDOWN)
                    self.registered_events.add(pg.KEYUP)

        self.widgets.append(w)

    def broadcast(self, event):
        if self.active:
            self.event_handler.broadcast(event)

    def render(self, screen):
        for w in self.widgets:
            w.render(screen)
