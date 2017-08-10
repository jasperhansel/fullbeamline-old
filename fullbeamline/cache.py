import os
import pickle
from fullbeamline.system_environment import system_environment


class Cache(object):

    max_file_number = system_environment.cache_limit

    def __enter__(self):
        try:
            with open('__fullbeamline/cache', 'rb') as f:
                self.next_file_number, self.cache_manifest = pickle.load(f)
        except FileNotFoundError:
            self.next_file_number = 1
            self.cache_manifest = {}
        return self

    def __exit__(self, *args):
        with open('__fullbeamline/cache', 'wb+') as f:
            pickle.dump((self.next_file_number, self.cache_manifest), f)

    def load(self, parameters):
        try:
            file_number = self.cache_manifest[parameters]
            os.link('__fullbeamline/cached_particles_{}'.format(file_number), '__fullbeamline/particles')
            return True
        except KeyError:
            return False

    def dump(self, parameters):
        if self.next_file_number <= self.max_file_number:
            os.link('__fullbeamline/particles', '__fullbeamline/cached_particles_{}'.format(self.next_file_number))
            self.cache_manifest[parameters] = self.next_file_number
            self.next_file_number += 1
