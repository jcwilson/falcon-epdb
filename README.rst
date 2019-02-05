###########
falcon-epdb
###########

|pypi| |src| |build| |coverage| |docs| |license| |black|

A `Falcon middleware`__ that wraps the excellent `epdb`_ tool and allows one to connect to a running Falcon app and use interactive debugging to step through the code.

Better documentation can be found at `readthedocs`_.

Source code can be found on GitHub at `jcwilson/falcon-epdb`__.

__ Falcon_middleware_

.. _Falcon_middleware: https://falcon.readthedocs.io/en/stable/api/middleware.html

__ jcwilson_falcon_epdb_

.. _jcwilson_falcon_epdb: https://github.com/jcwilson/falcon-epdb

.. _readthedocs: https://falcon-epdb.readthedocs.io


************
Installation
************
If you are only planning on debugging in a development environment where access to your service is restricted to you or trusted partners, you may find the `Base64`_ backend sufficient to your purposes. You can just install the library as you would any Python library.

**requirements.txt**

.. code-block:: text

  falcon-epdb

**pip**

.. code-block:: bash

  pip install falcon-epdb

**poetry**

.. code-block:: bash

  poetry add falcon-epdb

However, if you need a little more security, you can use one of the other authenticated backends (`Fernet`_, `JWT`_). Choose the one that best fits your use case and install it as a Python `extra`_.

**requirements.txt**

.. code-block:: text

  falcon-epdb[fernet]

**pip**

.. code-block:: bash

  pip install falcon-epdb[fernet, jwt]

**poetry**

.. code-block:: bash

  poetry add falcon-epdb[jwt]

.. _extra: https://www.python.org/dev/peps/pep-0508/#extras


*****
Usage
*****

This library adds a middleware to your Falcon API stack, and as such will run for all requests, save those excluded by ``exempt_methods`` provided to the ``EPDBServer`` constructor. If it detects a well-formed (and possibly authenticated) ``X-EPDB`` header on the request it will start the `epdb`_ server on the configured port and block until it establishes a connection from an `epdb`_ client, at which point processing continues but under the control of the remote debugging session.

Subsequent requests with an acceptable header will reuse the client connection and automatically drop into the remote debugging session again.

Configuring the middleware
==========================
The ``EPDBServe<falcon_epdb.EPDBServe>`` middleware accepts a handful of parameters. The most important are the ``backend`` and ``serve_options`` parameters. The ``backend`` determines how a request is examined for the "secret knock" to start the remote debugging server. The included implementations assume a well-formed ``X-EPDB`` header, but nothing precludes you from sub-classing ``EPDBBackend<falcon_epdb.EPDBBackend>`` and implementing your own.

The ``serve_options`` are options that are passed through to the ``epdb.serve()`` call. See `Backends`_ for details on how to add this middleware to your API.

Constructing the ``X-EPDB`` header
==================================

The content of the header is as follows:

.. code-block:: json

  {
    "epdb": {}
  }

Depending on the backend in use, one should encode this content into the appropriate header-safe value. Then append this value to the name of the backend.

.. code-block:: text

  X-EPDB: Base64 eyJlcGRiIjoge319

Connecting the client
=====================
Example code for connecting to the waiting port:

.. code-block:: python

  import epdb

  edpb.connect(host=<host>, port=9000)


.. _epdb: https://pypi.org/project/epdb/

Backends
========

Base64
------
**Server side configuration**

.. code-block:: python

  epdb_middleware = EPDBServe(
      backend=Base64Backend(),
      serve_options={'port': 9000})
  api = falcon.API(middleware=[epdb_middleware])

**Crafting an appropriate header**

.. code-block:: python

  import base64
  import json

  header_content = base64.b64encode(json.dumps({'epdb': {}}).encode()).decode()
  header_value = 'Base64 {}'.format(header_content)

Fernet
------
**Server side configuration**

.. code-block:: python

  fernet_key = Fernet.generate_key()  # The shared key
  epdb_middleware = EPDBServe(
      backend=FernetBackend(key=fernet_key),
      serve_options={'port': 9000})
  api = falcon.API(middleware=[epdb_middleware])

**Crafting an appropriate header**

.. code-block:: python

  import json
  from cryptography.fernet import Fernet

  f = Fernet(<fernet_key>)  # Key configured on the server
  header_content = f.encrypt(json.dumps({'epdb': {}}).encode()).decode()
  header_value = 'Fernet {}'.format(header_content)

JWT
------
**Server side configuration**

.. code-block:: python

  jwt_key = uuid.uuid4().hex  # The shared key
  epdb_middleware = EPDBServe(
      backend=JWTBackend(key=jwt_key),
      serve_options={'port': 9000})
  api = falcon.API(middleware=[epdb_middleware])

**Crafting an appropriate header**

.. code-block:: python

  import jwt

  header_content = jwt.encode({'epdb': {}}, <jwt_key>, algorithm='HS256').decode()
  header_value = 'JWT {}'.format(header_content)


***************
Troubleshooting
***************
You must be sure to allow access to the configured port on your host. Be sure to check your security groups and firewall rules.

Configure your web app to only run one worker process. If you have multiple workers, only the first one will be able to serve on the configured port. If this is not possible you will have to take steps to ensure that all requests that wish to use the remote debugging port are routed to the same worker. This will depend heavily on your HTTP stack and is beyond the scope of this documentation.

Be sure to up your request timeout limit to something on the order of minutes so that the HTTP server doesn't close your request connection or kill your worker process while you're debugging.

You may need to provide the ``HTTP-`` prefix on your ``X-EPDB`` header for it to be handled correctly. So instead of sending ``X-EPDB``, you would send ``HTTP-X-EPDB``.

.. |pypi| image:: https://badge.fury.io/py/falcon-epdb.svg
    :target: https://badge.fury.io/py/falcon-epdb
    :alt: Build version

.. |build| image:: https://travis-ci.org/jcwilson/falcon-epdb.svg?branch=master
  :target: https://travis-ci.org/jcwilson/falcon-epdb
  :alt: Build status

.. |coverage| image:: https://coveralls.io/repos/github/jcwilson/falcon-epdb/badge.svg
  :target: https://coveralls.io/github/jcwilson/falcon-epdb
  :alt: Coverage status

.. |docs| image:: https://readthedocs.org/projects/falcon-epdb/badge/?version=latest
  :target: https://falcon-epdb.readthedocs.io/en/latest
  :alt: Documentation status

.. |license| image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.svg
  :target: https://opensource.org/licenses/BSD-3-Clause
  :alt: Coverage status

.. |src| image:: https://img.shields.io/badge/src-github-blue.svg
  :target: https://github.com/jcwilson/falcon-epdb
  :alt: Source code

.. |black| image:: https://img.shields.io/badge/code%20format-black-black.svg
  :target: https://pypi.org/project/black/
  :alt: Black code formatter
