from scripts.shapes import *
from scripts.gui import *


class Attachable:
    def __init__(self, position: pg.Vector2, rotation=0):
        self.position = position.copy()
        self.rotation = rotation

        self.attached_objs = []  # list[list[Attachable, displacement_vector]]

    def rotate(self, angle):
        self.rotation += angle
        self.rotation %= 360
        for obj in self.attached_objs:
            obj[1] = obj[1].rotate(angle)
            obj[0].move_to(self.position + obj[1])
            obj[0].rotate(angle)

        self.rotate_subclass(angle)

    def move_to(self, position):
        displace = position - self.position
        self.displace(displace)

    def displace(self, offset):
        self.position += offset
        for obj in self.attached_objs:
            obj[0].displace(offset)
        self.displace_subclass(offset)

    def rotate_subclass(self, angle):
        pass

    def displace_subclass(self, offset):
        pass

    def attach(self, obj):
        self.attached_objs.append([obj, obj.position - self.position])

    def detach(self, obj):
        for o in self.attached_objs:
            if o[0] == obj:
                self.attached_objs.remove(o)
                break


class Interactable(Attachable):
    all_instances = []

    def __init__(self, position, rotation, *poly_args):
        Interactable.all_instances.append(self)
        super().__init__(position, rotation)
        if poly_args[0]:
            self.polygon: Polygon = Polygon(position, rotation, *poly_args)

    def check_interaction(self, sp, ep):
        coll = self.polygon.line_collide(sp, ep)
        if coll:
            return self, coll[0], coll[1]
        else:
            return False

    def check_selection(self, pos):
        pass

    @staticmethod
    def interact(ray, line: Line, position: pg.Vector2):
        reflected = ray.reflect(line.get_normal(), position)
        reflected.target = None
        return reflected

    @staticmethod
    def check_collision(sp, ep):
        for i in Interactable.all_instances:
            inter =  i.check_interaction(sp, ep)
            if inter:
                return inter
        return False

    @staticmethod
    def create_object():
        pass


class Instrument(Attachable):

    def __init__(self, position, rotation=0):
        # create button
        super().__init__(position, rotation)

    def update(self):
        pass

    def check_selection(self, pos):
        pass

    @staticmethod
    def create_object():
        pass


class Laser(Attachable):
    def __init__(self, color: pg.Color, position, direction: pg.Vector2):
        super().__init__(position, direction.angle_to(pg.Vector2(1, 0)))
        self.color = color
        self.direction = direction.normalize()
        self.power = laser_max_pow

        self.target: pg.Vector2 | None = None

        self.raylets: dict[Line, Laser] = {}

    def raycast(self):
        if not self.power:
            return

        if self.target:
            return

        target = self.position.copy()
        collision: list[Interactable, Line] | bool = Interactable.check_collision(self.position, target)

        while not collision:
            collision = Interactable.check_collision(self.position, target)

            if not (0 < target.x < win_width and
                    0 < target.y < win_height):
                break

            target += self.direction
        else:
            self.raylets[collision[1]] = collision[0].interact(self, collision[1], collision[2] - self.direction*2)
            self.raylets[collision[1]].power = self.power-1
            target = collision[2]

        for r in self.raylets.values():
            r.raycast()

        self.target = target

    def reflect(self, normal: pg.Vector2, origin):
        return Laser(self.color, origin, self.direction.reflect(normal))

    def rotate_subclass(self, angle):
        self.reset()
        self.direction = self.direction.rotate(angle)

    def displace_subclass(self, offset):
        self.reset()

    def reset(self):
        self.raylets.clear()
        self.target = None

    def render(self, screen: pg.Surface, flags=0):

        if not self.power:
            return

        if not self.target:
            self.raycast()

        middle = (self.position + self.target) / 2
        pos_off = self.position - middle
        tar_off = self.target - middle
        laser_vec = self.target - self.position
        surf = pg.Surface((abs(laser_vec.x) + 5, abs(laser_vec.y) + 5), pg.SRCALPHA)
        rect = surf.get_rect()
        rect.center = middle
        mid = pg.Vector2(surf.get_size()) / 2

        pg.draw.line(surf, self.color, mid + pos_off, mid + tar_off, laser_width)
        screen.blit(surf, rect, special_flags=pg.BLEND_RGBA_ADD)

        for r in self.raylets.values():
            r.render(screen, flags)

    def shader(self, screen, flags=0):

        if not self.power:
            return

        if not self.target:
            self.raycast()

        middle = (self.position + self.target) / 2
        pos_off = self.position - middle
        tar_off = self.target - middle
        laser_vec = self.target - self.position
        surf = pg.Surface((
            abs(laser_vec.x) + shader_steps ** shader_spread, abs(laser_vec.y) + shader_steps ** shader_spread
        ), pg.SRCALPHA)

        rect = surf.get_rect()
        rect.center = middle
        mid = pg.Vector2(surf.get_size()) / 2

        color = pg.Color(*tuple(self.color))

        for i in range(shader_steps, 0, -1):
            color.a = int((shader_steps - i) / shader_steps * 100)
            pg.draw.line(surf, color, mid + pos_off, mid + tar_off, int(2 * laser_width + i ** shader_spread))

        screen.blit(surf, rect, special_flags=pg.BLEND_RGBA_ADD)
        surf.set_colorkey(color)
        screen.blit(surf, rect)

        for r in self.raylets.values():
            r.shader(screen, flags)

    def get_length(self):
        return (self.target - self.position).magnitude() if self.target else 0


class LaserGroup(Attachable):
    def __init__(self, size, color, position, direction: pg.Vector2):
        self.size = size
        self.direction = direction
        self.color = color
        self.perpendicular = direction.rotate(90).normalize()

        super().__init__(position, direction.angle_to(pg.Vector2(1, 0)))

        for i in range(-size + 1, size):
            self.attach(Laser(color, position + i * (laser_width - laser_offset) * self.perpendicular, direction))

    def reset(self):
        for i in self.attached_objs:
            i[0].reset()

    def rotate_subclass(self, angle):
        self.perpendicular = self.perpendicular.rotate(angle)
        self.direction = self.direction.rotate(angle)

    def change_color(self, color):
        self.color = color
        for l, pos in self.attached_objs:
            l.color = color

    def increase_size(self, ds=1):
        for i in range(ds):
            self.attach(Laser(
                self.color,
                self.position + self.size * ((laser_width - laser_offset) * self.perpendicular) + (
                            i * (laser_width - laser_offset) * self.perpendicular) / 2,
                self.direction))
            self.attach(Laser(
                self.color,
                self.position - self.size * ((laser_width - laser_offset) * self.perpendicular) - (
                            i * (laser_width - laser_offset) * self.perpendicular) / 2,
                self.direction))
        self.size += ds

    def decrease_size(self, ds=1):
        if self.size - ds < 1:
            return False
        self.attached_objs = self.attached_objs[:-2 * ds]
        self.size -= ds

        return True

    def raycast(self):
        for l in self.attached_objs:
            l[0].raycast()

    def render(self, screen: pg.Surface, light_scrn, simulate, flags=0):

        for l, pos in self.attached_objs:
            pg.draw.circle(screen, l.color, self.position + pos, 2)
            if simulate:
                l.render(light_scrn)

    def shader(self, shader_screen, flags=0):
        for l, pos in self.attached_objs:
            l.shader(shader_screen, flags)


class PolyMirror(Interactable):

    icon = 'medium.png'

    def __init__(self, position, rotation, vertex_offsets: list[pg.Vector2]):
        super().__init__(position, rotation, vertex_offsets, mirror_color)
        self.attach(self.polygon)

        self.custom_frame = Frame(win_width, win_height, pg.Vector2(0, 0))
        self.selected_vertex = None
        self.vertices = {}

        self.custom_frame.add_widget(Image(pg.Vector2(self.position), 15, 15, 'cursor.png'))

        for i in range(len(self.polygon.vertex_offsets)):
            self.create_vertex_button(i)
        self.custom_frame.registered_events.add(pg.MOUSEBUTTONDOWN)
        self.custom_frame.event_handler.register(pg.MOUSEBUTTONDOWN, self.add_vertex)

    def render(self, screen: pg.Surface, light_scrn, simulate=False):
        self.polygon.render(screen)

    def shader(self, shader_scrn):
        pass

    def align_buttons(self):
        for k in self.vertices:
            self.vertices[k].position =  self.position + self.polygon.get_vertex_by_reference(k)
            self.vertices[k].rect.center = self.vertices[k].position

    def increase_size(self):
        self.polygon.increase_size()
        self.align_buttons()

    def decrease_size(self):
        self.polygon.decrease_size()
        self.align_buttons()

    def rotate_subclass(self, angle):
        self.align_buttons()

    def displace_subclass(self, offset):
        for w in self.custom_frame.widgets:
            w.position += offset
            w.rect.center = w.position

    def check_selection(self, pos):
        return self.polygon.collide_point(pos)

    def select_vertex(self, key):
        self.selected_vertex = key

    def move_vertex(self, *args):
        if self.selected_vertex:
            pos = pg.Vector2(pg.mouse.get_pos())
            v=self.polygon.get_vertex_by_reference(self.selected_vertex)
            v-=v
            v += pos - self.position
            self.vertices[self.selected_vertex].position = pos
            self.vertices[self.selected_vertex].rect.center = pos

    def delete_vertex(self, *args):
        if self.selected_vertex:
            if not self.polygon.delete_vertex(self.selected_vertex):
                return
            self.custom_frame.widgets.remove(self.vertices[self.selected_vertex])
            del self.vertices[self.selected_vertex]
            self.deselect_vertex()

    def create_vertex_button(self, i):
        key = self.polygon.refer_vertex(i)
        v = self.polygon.vertex_offsets[i]
        buttn = ImageButton(self.polygon.position + v, 10, 10,
                            lambda k=key: self.select_vertex(k), self.deselect_vertex,
                            image='corner.png')
        buttn.triggers[pg.MOUSEMOTION].append(('n', self.move_vertex))
        buttn.triggers[pg.K_d].append(('k', self.delete_vertex, None, False))

        self.vertices[key] = buttn
        self.custom_frame.add_widget(buttn)

    def add_vertex(self, event):
        if not self.selected_vertex:
            if event.button == pg.BUTTON_RIGHT:
                pos = pg.Vector2(pg.mouse.get_pos())

                self.create_vertex_button(self.polygon.add_vertex(pos))

    def deselect_vertex(self):
        self.selected_vertex = None
        self.polygon.update_polygon()

    def render_mask(self, surf):
        l = self.polygon.vertex_offsets
        for i in range(len(self.polygon.vertex_offsets)):
            v, w = l[i], l[(i + 1) % (len(l))]
            pg.draw.line(surf, white, self.position + v, self.position + w, poly_borderwidth+10)

    def get_arguments(self):
        return 'pom', ('v', self.position), ('u', self.rotation), ('l[v]', self.polygon.vertex_offsets)

    @staticmethod
    def create_object():
        return PolyMirror(pg.Vector2(win_width//2, win_height//2), 0,
                          [pg.Vector2(20, 0).rotate(i*90) for i in range(4)])


class PlaneMirror(Interactable):

    icon = 'mirror.png'

    def __init__(self, position, rotation, length):
        super().__init__(position, rotation, [], mirror_color)
        direc = pg.Vector2(1, 0).rotate(rotation)
        self.line = Line(self.position+direc*length/2, self.position-direc*length/2)
        self.attach(self.line)
        self.interacting: list[Laser] = []

        self.custom_frame = Frame(200, win_height, pg.Vector2(win_width-200, 0))

    def render(self, screen: pg.Surface, light_scrn, simulate=False):
        pg.draw.line(screen, mirror_color, self.line.start_pos, self.line.end_pos, mirror_width)

    def shader(self, screen):
        pass

    def check_interaction(self, sp, ep):
        coll = self.line.intersect_line(sp, ep)
        if coll:
            return self, self.line, coll
        return False

    def increase_size(self):
        self.line.increase_size()

    def decrease_size(self):
        self.line.decrease_size()

    def check_selection(self, pos):
        return self.line.collide_point(pos.x, pos.y)

    def render_mask(self, surf):
        mid = self.position
        s , e = (self.line.start_pos - self.line.position), (self.line.end_pos - self.line.position)

        pg.draw.line(
            surf,
            pg.Color(255, 255, 255),
            mid + s + s.normalize()*5,
            mid + e + e.normalize()*5,
            mirror_width + 10)

    def get_arguments(self):
        return 'plm', ('v', self.position), ('u', self.rotation), ('u', self.line.get_length())

    @staticmethod
    def create_object():
        return PlaneMirror(pg.Vector2(win_width // 2, win_height // 2), 0, 100)


class Pointer(Instrument):

    icon = 'pointer.png'

    def __init__(self, position, rotation, color, size):
        self.width, self.height = (50, ((laser_width + 2) * size) + 15)
        self.laser_grp = LaserGroup(size, color, position + pg.Vector2(self.width // 2, 0).rotate(rotation),
                                    pg.Vector2(1, 0).rotate(rotation))
        super().__init__(position, rotation)
        self.polygon = Rectangle(self.width, self.height, position, rotation, pointer_color)
        self.attach(self.laser_grp)
        self.attach(self.polygon)

        self.custom_frame = Frame(200, win_height, pg.Vector2(win_width-200, 0))
        self.custom_frame.add_widget(ColorPicker(
            pg.Vector2((self.custom_frame.position.x + 100, win_height//2)),
            win_height - 250,
            self.laser_grp.change_color,
            color
        ))

    def render(self, screen: pg.Surface, light_scrn, simulate=False):
        self.polygon.render(screen)
        self.laser_grp.render(screen, light_scrn, simulate)

        if simulate:
            self.raycast()

    def reset(self):
        self.laser_grp.reset()

    def shader(self, shader_scrn, flags=0):
        self.laser_grp.shader(shader_scrn, flags)

    def raycast(self):
        self.laser_grp.raycast()

    def increase_size(self):
        self.laser_grp.increase_size()
        self.detach(self.polygon)
        self.width, self.height = (50, (2 * (laser_width - laser_offset) * self.laser_grp.size) + 15)
        self.polygon = Rectangle(self.width, self.height, self.position, self.rotation, pg.Color(0, 0, 0))
        self.attach(self.polygon)

    def decrease_size(self):
        if not self.laser_grp.decrease_size():
            return
        self.detach(self.polygon)
        self.width, self.height = (50, (2 * (laser_width - laser_offset) * self.laser_grp.size) + 15)
        self.polygon = Rectangle(self.width, self.height, self.position, self.rotation, pg.Color(0, 0, 0))
        self.attach(self.polygon)

    def check_selection(self, pos):
        return self.polygon.collide_point(pos)

    def render_mask(self, surf):
        l = self.polygon.vertex_offsets
        for i in range(len(self.polygon.vertex_offsets)):
            v, w = l[i], l[(i + 1) % (len(l))]
            pg.draw.line(surf, white, self.position + v, self.position + w, poly_borderwidth + 5)

    def get_arguments(self):
        return 'ptr', ('v', self.position), ('u', self.rotation), ('u', self.laser_grp.color), ('u', self.laser_grp.size)

    @staticmethod
    def create_object():
        return Pointer(pg.Vector2(win_width // 2, win_height // 2), 0, pg.Color(255, 0, 0), 1)


Objects = Interactable | Instrument
Interactives = PolyMirror | PlaneMirror