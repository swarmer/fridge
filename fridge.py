__all__ = ['Fridge']

import json
import errno
import functools


class Fridge(dict):
    """
    Fridge is a subclass of :class:`dict` and thus fully conforms to its interface.

    Fridge keeps an open file until it's closed, so you have to call :meth:`close`
    when you're done using it.

    Fridge implements :meth:`__enter__` and :meth:`__exit__` so you can use
    `with` statement.

    :param path: a path to a file that will be used to load and save the data
    :param file: a file object that will be used to load and save the data.
        This file object in not closed by fridge automatically.

    `path` and `file` arguments are mutually exclusive
    """

    def __init__(self, path=None, file=None):
        if path is None and file is None:
            raise ValueError('No path or file specified')
        elif path is not None and file is not None:
            raise ValueError('Only path or only file can be passed')
        if file is not None:
            self.file = file
            self.close_file = False
        else:
            try:
                self.file = open(path, 'r+')
            except IOError as e:
                if e.errno == errno.ENOENT:
                    self.file=open(path, 'w+')
                else:
                    raise
            self.close_file = True

        #: True after :meth:`close` is called, False otherwise.
        self.closed = False

        self.load()

    def check_open(self):
        if self.closed:
            raise ValueError('Operation on a closed fridge object')

    def load(self):
        """
        Force reloading the data from the file.
        All data in the in-memory dictionary is lost.
        This method is called automatically by the constructor, normally you
        don't need to call it.
        """
        self.check_open()
        try:
            data = json.load(self.file)
        except ValueError:
            data = {}
        if not isinstance(data, dict):
            raise ValueError('Root JSON type must be dictionary')
        self.clear()
        self.update(data)

    def save(self):
        """
        Force saving the dictionary to the file.
        All data in the file is lost.
        This method is called automatically by :meth:`close`.
        """
        self.check_open()
        self.file.truncate(0)
        self.file.seek(0)
        json.dump(self, self.file)

    def close(self):
        """
        Close the fridge.
        Calls :meth:`save` and closes the underlying file object unless
        an already open file was passed to the constructor.
        This method has no effect if the file is already closed.

        After the fridge is closed :meth:`save` and :meth:`load` will raise an exception
        but you will still be able to use it as an ordinary dictionary.
        """
        if not self.closed:
            self.save()
            if self.close_file:
                self.file.close()
        self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
        return False
    
    def __del__(self):
        self.close()
