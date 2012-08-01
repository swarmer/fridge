import unittest
import io
from json import loads

from fridge import Fridge


class FridgeTest(unittest.TestCase):

    def setUp(self):
        self.buf = io.StringIO()

    def rewind(self):
        self.buf.seek(0)

    def test_file(self):
        with Fridge(file=self.buf) as fridge:
            pass
        self.rewind()
        with Fridge(file=self.buf) as fridge:
            pass
        self.assertEqual(self.buf.getvalue(), '{}')

    def test_insertion(self):
        with Fridge(file=self.buf) as fridge:
            fridge['a'] = 'a'
        self.assertEqual(self.buf.getvalue(), '{"a": "a"}')
        self.rewind()
        with Fridge(file=self.buf) as fridge:
            fridge['b'] = 'b'
            fridge['a'] = 'new_a'
        self.assertEqual(loads(self.buf.getvalue()), {'a': 'new_a', 'b': 'b'})

    def test_deletion(self):
        with Fridge(file=self.buf) as fridge:
            fridge['a'] = 'a'
            fridge['b'] = 'b'
            fridge['c'] = 'c'
        self.rewind()
        with Fridge(file=self.buf) as fridge:
            fridge['b'] = 'new_b'
            del fridge['c']
        self.assertEqual(loads(self.buf.getvalue()), {'a': 'a', 'b': 'new_b'})
    
    def test_load(self):
        with Fridge(file=self.buf) as fridge:
            fridge['a'] = 'a'
            self.assertEqual(fridge, {'a': 'a'})
            self.buf.truncate(0)
            self.rewind()
            fridge.load()
            self.assertEqual(fridge, {})

    def test_types(self):
        with Fridge(file=self.buf) as fridge:
            fridge['str'] = 'a'
            fridge['int'] = 42
            fridge['float'] = 3.14
            fridge['list'] = [{'num': 2}, [], 8.65]
        self.rewind()
        with Fridge(file=self.buf) as fridge:
            data = {'str': 'a',
                    'int': 42,
                    'float': 3.14,
                    'list': [{'num': 2}, [], 8.65]}
            self.assertEqual(fridge, data)

    def test_close(self):
        fridge = Fridge(file=self.buf)
        fridge['a'] = 'a'
        fridge.close()
        self.assertTrue(fridge.closed)
        self.assertFalse(self.buf.closed)
        self.assertEqual(self.buf.getvalue(), '{"a": "a"}')
        with self.assertRaises(ValueError):
            fridge.load()
        with self.assertRaises(ValueError):
            fridge.save()
