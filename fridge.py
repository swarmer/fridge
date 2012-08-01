"""
A persistent dict-like storage that uses JSON to store its contents.
"""

import json
import errno


class Fridge(dict):

    def __init__(self, path=None, file=None):
        if path is None and file is None:
            raise ValueError('No path or file specified')
        elif path is not None and file is not None:
            raise ValueError('Only path or only file can be passed')
        if file is not None:
            self.file = file
        else:
            try:
                self.file = open(path, 'r+')
            except IOError as e:
                if e.errno == errno.ENOENT:
                    self.file=open(path, 'w+')
                else:
                    raise
        self.load()
        self.closed = False

    def load(self):
        try:
            data = json.load(self.file)
        except ValueError:
            data = {}
        if not isinstance(data, dict):
            raise ValueError('Root JSON type must be dictionary')
        self.update(data)

    def save(self):
        if not self.file.closed:
            self.file.truncate(0)
            self.file.seek(0)
            json.dump(self, self.file)

    def close(self):
        self.save()
        self.file.close()
        self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
        return False
    
    def __del__(self):
        self.close()
