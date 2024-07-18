from config import *


class Line:

    def __init__(self, start_pos: pg.Vector2, end_pos: pg.Vector2):
        self.start_pos = start_pos
        self.end_pos = end_pos

        self.position = (self.start_pos + self.end_pos) / 2

    def get_normal(self):
        return (self.start_pos - self.end_pos).rotate(90).normalize()

    def collide_point(self, x, y):
        a = (self.start_pos - self.end_pos).magnitude()/2
        angle = (self.start_pos - self.end_pos).as_polar()[1]
        return ((
                (x-self.position.x)*cos(angle) + (y-self.position.y)*sin(angle)
        )**2/a**2 + (
                (x-self.position.x)*sin(angle) - (y-self.position.y)*cos(angle)
        )**2/10**2) < 1

    def increase_size(self, ds=1):
        self.start_pos += (self.start_pos - self.position).normalize() * ds
        self.end_pos += (self.end_pos - self.position).normalize() * ds

    def decrease_size(self, ds=1):
        if (self.start_pos - self.end_pos).magnitude() - 2*ds <= 10:
            return
        self.start_pos -= (self.start_pos - self.position).normalize() * ds
        self.end_pos -= (self.end_pos - self.position).normalize() * ds

    def rotate(self, angle):
        self.start_pos = (self.start_pos - self.position).rotate(angle) + self.position
        self.end_pos = (self.end_pos - self.position).rotate(angle) + self.position

    def displace(self, offset):
        self.start_pos+=offset
        self.position += offset
        self.end_pos+=offset

    def move_to(self, position):
        self.displace(position - self.position  )

    def distance_to(self, point : pg.Vector2):
        return abs((self.start_pos - point).dot(self.get_normal()))

    def intersect_line(self, sp, ep):

        x1, y1, x2, y2 = tuple(sp) + tuple(ep)
        x3, y3, x4, y4 = tuple(
            self.start_pos + (self.start_pos - self.position).normalize() * 2
        ) + tuple(
            self.end_pos + (self.end_pos - self.position).normalize() * 2
        )

        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if den == 0:
            return

        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
        u = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / den
        if 0 < t < 1 and 0 < u < 1:
            return pg.Vector2(x1 + t * (x2 - x1),
                                  y1 + t * (y2 - y1))


class Polygon(pg.sprite.Sprite):

    def __init__(self, position, rotation, vertex_offsets: list[pg.Vector2], color, *groups):
        super().__init__(*groups)

        self.position = position.copy()
        self.rotation = 0
        self.vertex_offsets = vertex_offsets
        self.color = pg.Color(*color)
        self.edges: list[Line] = []
        self.children = []

        self.vertex_references = {}

        self.is_anchored = False

        self.image = pg.Surface((10, 10))
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)

        self.update_polygon()
        self.rotate(rotation)

    def get_com(self):
        return sum(self.vertex_offsets, start=pg.Vector2())/len(self.vertex_offsets)

    def update_polygon(self):
        if not len(self.vertex_offsets): return

        # self.vertex_offsets.sort(
        #     key=lambda v: get_vector_angle(v)
        # )

        self.image = pg.Surface(
            (2 * abs(max(self.vertex_offsets, key=lambda o: abs(o.x)).x) + 2*poly_borderwidth,
             2 * abs(max(self.vertex_offsets, key=lambda o: abs(o.y)).y) + 2*poly_borderwidth),
            pg.SRCALPHA)

        self.rect = self.image.get_rect()

        self.edges.clear()
        center = pg.Vector2((self.rect.width // 2, self.rect.height // 2))

        pg.draw.polygon(self.image, self.color, [center + v for v in self.vertex_offsets])

        for i in range(len(self.vertex_offsets)):
            line = Line(
                self.vertex_offsets[i], self.vertex_offsets[(i + 1) % (len(self.vertex_offsets))])

            self.edges.append(line)

        mask = pg.mask.from_surface(self.image).to_surface()
        mask.set_colorkey((255, 255, 255))

        border = pg.Surface(mask.get_size())
        border.fill(self.color.lerp((0, 0, 0), 0.5))
        border.blit(mask, (0, 0))
        border.set_colorkey((0, 0, 0))

        for i in range(pol_borderclarity):
            a = i * 2 * pi / pol_borderclarity
            self.image.blit(border, poly_borderwidth * pg.Vector2((cos(a), sin(a))))

        pg.draw.polygon(self.image, self.color, [center + v for v in self.vertex_offsets])
        self.rect.center = self.position
        self.mask = pg.mask.from_surface(self.image)

    def displace(self, offset: pg.Vector2):
        self.position += offset
        self.update_polygon()

    def move_to(self, pos: pg.Vector2):
        self.displace(pos - self.rect.center)

    def rotate(self, angle_d=90, angle_r=None):
        angle = angle_r * 180 / pi if angle_r else angle_d

        angle%=360

        for i, v in enumerate(self.vertex_offsets):
            self.vertex_offsets[i] = v.rotate(angle)

        self.update_polygon()

    def increase_size(self, ds = 1):
        for o in self.vertex_offsets:
            wid = self.image.get_width()
            hei = self.image.get_height()

            nx = (o.x * (wid+2*ds))/wid
            ny = (o.y * (hei + 2*ds))/hei

            o -= o
            o += pg.Vector2((nx, ny))

        self.update_polygon()

    def decrease_size(self, ds = 1):
        if min(self.vertex_offsets, key = lambda v: v.magnitude()).magnitude() - ds < 10:
            return False
        for o in self.vertex_offsets:
            wid = self.image.get_width()
            hei = self.image.get_height()

            nx = (o.x * (wid - 2 * ds)) / wid
            ny = (o.y * (hei - 2 * ds)) / hei

            o -= o
            o += pg.Vector2((nx, ny))

        self.update_polygon()

        return True

    def render(self, screen: pg.Surface, flags=0):

        screen.blit(self.image, self.rect, special_flags=flags)

    def collide_point(self, *pos):
        point = pg.Vector2(*pos)
        return bool(self.rect.collidepoint(point) and self.mask.get_at(point - self.rect.topleft))

    def closest_line(self, p):
        return min(self.edges, key=lambda l: l.distance_to(p-self.position))

    def line_collide(self, sp, ep):
        if not self.rect.collidepoint(ep):
            return
        for l in self.edges:
            coll = l.intersect_line(sp-self.position, ep-self.position)
            if coll:
                return l, coll + self.position
        else:
            return False

    def add_vertex(self, pos):
        i, dist = -1, -1
        for index in range(len(self.vertex_offsets)):
            mid = (self.vertex_offsets[index] + self.vertex_offsets[(index + 1) % (len(self.vertex_offsets))])/2
            d = (pos-self.position - mid).magnitude()
            if d < dist or dist < 0:
                dist = d
                i = index

        offset = (self.vertex_offsets[i] + self.vertex_offsets[(i + 1) % (len(self.vertex_offsets))]) / 2

        for k in self.vertex_references:
            if self.vertex_references[k] > i:
                self.vertex_references[k] += 1

        self.vertex_offsets.insert(i + 1, offset)
        self.update_polygon()

        return i+1

    def refer_vertex(self, index):
        key = str(random()*10**8)[:8]
        self.vertex_references[key] = index

        return key

    def get_vertex_by_reference(self, key):
        return self.vertex_offsets[self.vertex_references.get(key, None)]

    def delete_vertex(self, key):

        if len(self.vertex_offsets) == 3:
            return False

        i = self.vertex_references[key]
        self.vertex_offsets.pop(i)
        del self.vertex_references[key]
        for k in self.vertex_references:
            if self.vertex_references[k] > i:
                self.vertex_references[k] -= 1

        self.update_polygon()

        return True

    def copy(self):
        return Polygon(
            pg.Vector2(self.position.x, self.position.y),
            self.rotation,
            [pg.Vector2(tuple(v)) for v in self.vertex_offsets],
            pg.Color(tuple(self.color))
        )


class Rectangle(Polygon):

    def __init__(self, width, height, position, rotation, color, *groups):
        v_off = [(width // 2, height // 2), (-width // 2, height // 2), (-width // 2, -height // 2),
                 (width // 2, -height // 2)]

        super().__init__(position, rotation, [pg.Vector2(off) for off in v_off], color, *groups)
