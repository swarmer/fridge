# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from json import loads
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from fridge import Fridge


class FridgeTest(unittest.TestCase):

    def setUp(self):
        self.buf = StringIO()

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

    def test_update(self):
        with Fridge(file=self.buf) as fridge:
            fridge['n'] = 2
            fridge['l'] = []
        self.assertEqual(loads(self.buf.getvalue()), {'n': 2, 'l': []})
        self.rewind()
        with Fridge(file=self.buf) as fridge:
            fridge['n'] += 1
            fridge['l'].append('str')
        self.assertEqual(loads(self.buf.getvalue()), {'n': 3, 'l': ['str']})

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

    def test_unicode(self):
        with Fridge(file=self.buf) as fridge:
            fridge['str'] = 'a'
            fridge['кириллица'] = 'я люблю пельмени'
            fridge['mixed кодировка'] = 'смешанная encoding'
            fridge['list'] = [{'борщ': 'с капусткой, но не красный'}, [], 8.65]
        self.rewind()
        with Fridge(file=self.buf) as fridge:
            self.assertEqual(fridge['str'], 'a')
            self.assertEqual(fridge['кириллица'], 'я люблю пельмени')
            self.assertEqual(fridge['mixed кодировка'], 'смешанная encoding')
            self.assertEqual(fridge['list'],
                    [{'борщ': 'с капусткой, но не красный'}, [], 8.65])

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
