import pickle

from config import *
from pickle import load, dump
from scripts.objects import Pointer, PolyMirror, PlaneMirror


class InstanceManager:

    class_encs = {
        'ptr' : Pointer,
        'plm' : PlaneMirror,
        'pom' : PolyMirror
    }

    def __init__(self, sim):
        self.sim = sim

    def save_instance(self, objects, save_name):
        f = open(f'saves/{save_name}.lpi', 'wb')
        enc_objs = []
        for obj in objects:
            arguments = obj.get_arguments()
            enc_args = [arguments[0]]
            for arg in arguments[1:]:
                enc_args.append(self.encode_argument(*arg))

            enc_objs.append(enc_args)

        dump(enc_objs, f)

    def load_instance(self, save_name):
        try:
            f = open(f'saves/{save_name}.lpi', 'rb')
        except FileNotFoundError:
            dump([], open(f'saves/{save_name}.lpi', 'wb'))
            return []

        objects = load(f)
        loaded_objects = []
        for obj in objects:
            cl = InstanceManager.class_encs[obj[0]]
            args = []
            for arg in obj[1:]:
                args.append(self.decode_argument(*arg))

            loaded_objects.append(
                cl(*tuple(args))
            )

        return loaded_objects

    def encode_argument(self, form: str, obj):
        if form == 'u':
            return form, obj

        if form == 'v':
            return form, (obj.x, obj.y)

        if form[0] == 'l':
            lis = []
            for i in obj:
                lis.append(self.encode_argument(form[form.index('[')+1:form.index(']')], i))

            return form, lis

    def decode_argument(self, form: str, obj):
        if form == 'u':
            return obj

        if form == 'v':
            return pg.Vector2(obj)

        if form[0] == 'l':
            lis = []
            for i in obj:
                lis.append(self.decode_argument(*i))

            return lis
