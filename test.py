# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
import json
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

    def test_readonly(self):
        with Fridge(file=self.buf) as fridge:
            fridge['str'] = 'a'
            fridge['int'] = 42
        self.rewind()
        ro = Fridge.readonly(file=self.buf)
        self.assertEqual(ro['str'], 'a')
        self.assertEqual(ro['int'], 42)
        self.assertTrue(ro.closed)
        with self.assertRaises(ValueError):
            fridge.load()
        with self.assertRaises(ValueError):
            fridge.save()

    def test_json_args(self):
        _d = {}
        def dump_wrapper(*args, **kwargs):
            _d['dump_kwargs'] = kwargs
        def load_wrapper(*args, **kwargs):
            _d['load_kwargs'] = kwargs
            return {}
        _orig_dump = json.dump
        _orig_load = json.load
        json.dump = dump_wrapper
        json.load = load_wrapper
        try:
            dump_args = {'dump_test': 1}
            load_args = {'load_test': 2}
            with Fridge(file=self.buf, dump_args=dump_args,
                            load_args=load_args) as fridge:
                fridge['a'] = 1
            self.assertEqual(_d['dump_kwargs']['dump_test'], 1)
            self.assertEqual(_d['load_kwargs']['load_test'], 2)
        finally:
            json.dump = _orig_dump
            json.load = _orig_load

    def test_default(self):
        Fridge.default_args = {}
        with self.assertRaises(ValueError):
            fridge = Fridge()

        Fridge.default_args = {'file': self.buf}
        with Fridge() as fridge:
            fridge['a'] = 'a'
        self.assertEqual(self.buf.getvalue(), '{"a": "a"}')

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
