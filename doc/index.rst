.. Fridge documentation master file, created by
   sphinx-quickstart on Thu Aug  2 02:44:32 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Fridge's documentation!
==================================
Fridge is a persistent dict-like object useful for storing settings
or any other JSON-serializable data.

Fridge currently supports only Python 3.


Quick start
-----------
::

    from fridge import Fridge    

    with Fridge('/home/user/config') as fr:
        username = fr['username']
        password = fr['password']
        fr.setdefault('login_count', 0)
        fr['login_count'] += 1


Contents
--------
.. toctree::
    :maxdepth: 2

    api


Indices and tables
------------------
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
