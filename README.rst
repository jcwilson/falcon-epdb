falcon-epdb
===========

|build| |docs|


A `Falcon middleware`__ that allows one to connect to a running Falcon app and use interactive debugging to step through the code.

.. _Falcon_middleware: https://falcon.readthedocs.io/en/stable/api/middleware.html

__ Falcon_middleware_

API
----
.. autoclass:: falcon_epdb.EPDBServe
    :members:

.. autoclass:: falcon_epdb.FernetBackend
    :members:

.. autoclass:: falcon_epdb.JWTBackend
    :members:

.. autoclass:: falcon_epdb.EPDBBackend
    :members:

.. autoexception:: falcon_epdb.EPDBException

.. |build| image:: https://travis-ci.org/jcwilson/falcon-epdb.svg?branch=master
    :target: https://travis-ci.org/jcwilson/falcon-epdb

.. |docs| image:: https://readthedocs.org/projects/falcon-epdb/badge/?version=latest
    :target: https://falcon-epdb.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
