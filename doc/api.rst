API reference
=============
.. module:: fridge

.. autoclass:: Fridge
    :members:

    .. attribute:: static Fridge.default_args

        Arguments that are used if :class:`Fridge` is called
        without `path` or `file` arguments. Example::

            from fridge import Fridge

            Fridge.default_args['path'] = '/home/user/.settings.conf'


            with Fridge() as settings:
                settings['name'] = 'user'
