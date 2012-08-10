__all__ = ['Fridge']
__version__ = '0.2'

import json
import errno


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
    :param dump_args: dictionary of arguments that are passed to :func:`json.dump`.
    :param load_args: dictionary of arguments that are passed to :func:`json.load`.

    `path` and `file` arguments are mutually exclusive.
    """

    default_args = {}

    @classmethod
    def readonly(cls, *args, **kwargs):
        """
        Return an already closed read-only instance of Fridge.
        Arguments are the same as for the constructor.
        """
        fridge = cls(*args, **kwargs)
        fridge.close()
        return fridge

    @classmethod
    def _getdefault(cls):
        default = cls.default_args
        path = default.get('path')
        file = default.get('file')
        return path, file

    def __new__(cls, path=None, file=None, *args, **kwargs):
        if path is None and file is None:
            path, file = cls._getdefault()

        if path is None and file is None:
            raise ValueError('No path or file specified')
        elif path is not None and file is not None:
            raise ValueError('Only path or only file can be passed')

        fridge = super(Fridge, cls).__new__(cls)
        return fridge

    def __init__(self, path=None, file=None, dump_args=None, load_args=None):
        if path is None and file is None:
            path, file = self._getdefault()

        self.dump_args = dump_args or {}
        self.load_args = load_args or {}

        # so that __del__ doesn't try to close the file if its opening fails
        self.closed = True

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

    def _check_open(self):
        if self.closed:
            raise ValueError('Operation on a closed fridge object')

    def load(self):
        """
        Force reloading the data from the file.
        All data in the in-memory dictionary is discarded.
        This method is called automatically by the constructor, normally you
        don't need to call it.
        """
        self._check_open()
        try:
            data = json.load(self.file, **self.load_args)
        except ValueError:
            data = {}
        if not isinstance(data, dict):
            raise ValueError('Root JSON type must be dictionary')
        self.clear()
        self.update(data)

    def save(self):
        """
        Force saving the dictionary to the file.
        All data in the file is discarded.
        This method is called automatically by :meth:`close`.
        """
        self._check_open()
        self.file.truncate(0)
        self.file.seek(0)
        json.dump(self, self.file, **self.dump_args)

    def close(self):
        """
        Close the fridge.
        Calls :meth:`save` and closes the underlying file object unless
        an already open file was passed to the constructor.
        This method has no effect if the object is already closed.

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
