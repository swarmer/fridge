######
Fridge
######
.. image:: https://secure.travis-ci.org/swarmer/fridge.png?branch=master
Fridge is a persistent dict-like object that uses JSON to store its contents.

Fridge officially supports Python 3.3, 3.2 and 2.7.

Quick start
===========
::

    from fridge import Fridge

    with Fridge('/home/user/config') as fr:
        username = fr['username']
        password = fr['password']
        fr.setdefault('login_count', 0)
        fr['login_count'] += 1

Documentation
=============
http://fridge.readthedocs.org/

Installation
============
``pip install fridge``

Or just grab ``fridge.py``.

License
=======
MIT (see LICENSE.txt).
