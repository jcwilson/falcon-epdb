"""Remote debugging support for Falcon apps."""

__version__ = '0.1.0'

import json
from abc import ABCMeta, abstractmethod
from logging import getLogger

import epdb

try:
    from cryptography import fernet
except ImportError:
    pass

try:
    import jwt
except ImportError:
    pass


logger = getLogger(__name__)


class EPDBException(Exception):
    """Raised when an error occurs during the processing of an ``X-EPDB`` header."""

class EPDBServe(object):
    """A middleware to enable remote debuging via an `epdb`_ server.

    :param backend: An instance of the class that will validate and decode the ``X-EPDB`` header
    :param exempt_methods: HTTP methods which will be ignored by this middleware
    :param serve_options: Parameters passed-through to :func:`epdb.serve()`
    :type backend: EPDBBackend
    :type exempt_methods: iterable of strings
    :type serve_options: dictionary

    A client may include a special ``X-EPDB`` header containing an appropriately formed payload.
    If they do, the header will be passed to the configured backend for processing. If the
    payload passes authentication and meets the content requirements, the app will be begin
    listening for `epdb`_ client connections.

    A well-formed header has content simply of the form::

        {
            "epdb": {
                # optional
                "port": <port value>
            }
        }

    The encoding and encryption of this payload is determined by the :class:`EPDBBackend`
    provided to the middleware.

    .. _epdb: https://pypi.org/project/epdb/
    """

    def __init__(self, backend, exempt_methods=('OPTIONS',), serve_options=None):
        serve_options = serve_options or {}
        self.backend = backend
        self.exempt_methods = exempt_methods
        self.serve_options = serve_options

    def process_request(self, req, resp):
        """Check for a well-formed ``X-EPDB`` header and if present activate the `epdb`_ server.

        :param req: The Falcon request object
        :param resp: The Falcon response object (unused)

        This will block, waiting for an `epdb`_ client connection, the first time a valid
        header is received. Once the client is connected, subsequent passes will simply activate
        the connected client and drop it into the `epdb`_ shell.

        The header processing is delegated to the configured :class:`EPDBBackend`.
        """
        if req.method in self.exempt_methods:
            return

        try:
            header_data = self.backend.get_header_data(req)
            if header_data is not None:
                serve_options = self.serve_options.copy()
                serve_options.setdefault('port', header_data.get('port'))

                logger.debug('Serving epdb with options: {}', serve_options)
                epdb.serve(**serve_options)
        except EPDBException:
            # Probably got an invalid header value. Don't start the debugger.
            logger.exception('Attempted, but failed, to serve epdb')
        except Exception:
            logger.exception('Unexpected error when processing the X-EPDB header')


class EPDBBackend(object):
    """The abstract base class defining the header-processing backend interface.

    An inheriting subclass must define :meth:`decode_header_value`, but may define other methods
    if necessary. This class is structured to provide a balance of convenience and flexibility.
    """

    __metaclass__ = ABCMeta

    def get_header_data(self, req):
        """Process a request and return the contents of a conforming payload.

        :param req: The Falcon request object
        :type req: Request
        :returns: The paylod content or None
        :rtype: dictionary or None

        This implementation assumes that the payload is present on the ``X-EPDB`` header, but
        subclasses may override this method if their use-case demands it.

        If the request does not appear to be attempting begin a debugging session, this will
        return :obj:`None`.
        """
        epdb_header = req.headers.get('X-EPDB')
        if epdb_header:
            logger.debug('Found epdb header')
            header_content = self.decode_header_value(epdb_header)
            return self.validate_header_content(header_content)

    @abstractmethod
    def decode_header_value(self, epdb_header):
        """Process the ``X-EPDB`` header content.

        :param epdb_header: The content of the ``X-EPDB`` header
        :type epdb_header: string
        :returns: The decoded and decrypt header payload
        :rtype: dictionary

        This does not need to do any content validation, as that is handled in
        :meth:`validate_header_content`.
        """
        pass

    def validate_header_content(self, header_content):
        """Ensure that the decoded ``X-EPDB`` header content is well-formed.

        :param header_content: The decoded ``X-EPDB`` header content
        :type header_content: dictionary
        :returns: The value of the `epdb`_ key
        :rtype: dictionary
        :raises: EPDBException

        :obj:`header_content` must be of the form::

            {
                "epdb": {
                    # optional
                    "port": <port value>
                }
            }
        """
        if not isinstance(header_content, dict):
            raise EPDBException('Invalid X-EPDB content; must be a dictionary')

        if 'epdb' not in header_content:
            raise EPDBException('Invalid X-EPDB content; must contain key named "epdb"')

        if not isinstance(header_content['epdb'], dict):
            raise EPDBException('Invalid X-EPDB content; "epdb" key must map to a dictionary')

        return header_content['epdb']


class FernetBackend(EPDBBackend):
    """A Python cryptography-based backend that supports a pre-shared key (ie. password) protocol.

    :param key: The fernet key used to encrypt the header content
    :type key: bytes

    To generate the request header, one may do something like the following:

    .. code-block:: python

        import json
        from cryptography.fernet import Fernet

        key = Fernet.generate_key()
        f = Fernet(key)
        header_content = f.encrypt(json.dumps({'epdb': {}}).encode()).decode()
        header_value = 'Fernet {}'.format(header_content)

    .. note:: To use this backend, one must install the :mod:`cryptography` package. The easiest
        way to do this is to specify the ``[fernet]`` extra when adding the ``falcon-epdb``
        dependency to your project.

        .. code-block:: text
            :caption: **requirements.txt**

            falcon-epdb[fernet]
    """

    def __init__(self, key):
        try:
            self.fernet = fernet.Fernet(key)
        except NameError:
            raise ImportError('Missing optional [fernet] dependency')

    def decode_header_value(self, epdb_header):
        """Pull the encrypted data out of the header, if present.

        :param epdb_header: The content of the ``X-EPDB`` header.
        :type epdb_header: string
        :returns: The decoded and decrypt header payload
        :rtype: dictionary
        :raises: EPDBException

        It expects :obj:`epdb_header` to have the ``Fernet`` prefix.
        """
        try:
            scheme, payload = epdb_header.split(None, 1)
        except ValueError:
            raise EPDBException('Invalid X-EPDB value; must have two tokens')

        if scheme != 'Fernet':
            raise EPDBException('Invalid X-EPDB value; scheme must be Fernet')

        decrypted_bytes = self.fernet.decrypt(payload.encode())
        decrypted_string = decrypted_bytes.decode()
        return json.loads(decrypted_string)


class JWTBackend(EPDBBackend):
    """A JWT-based backend that supports a pre-shared key (ie. password) protocol.

    :param key: The JWT key used to encrypt the header content
    :type key: bytes

    To generate the request header, one may do something like the following:

    .. code-block:: python

        import jwt
        import uuid

        key = uuid.uuid4().hex
        header_content = jwt.encode({'epdb': {}}, key, algorithm='HS256').decode()
        header_value = 'JWT {}'.format(header_content)

    .. note:: To use this backend, one must install the :mod:`PyJWT` package. The easiest
        way to do this is to specify the ``[jwt]`` extra when adding the ``falcon-epdb``
        dependency to your project.

        .. code-block:: text
            :caption: **requirements.txt**

            falcon-epdb[jwt]
    """

    def __init__(self, key):
        try:
            jwt
        except NameError:
            raise ImportError('Missing optional [jwt] dependency')

        self.key = key

    def decode_header_value(self, epdb_header):
        """Pull the encrypted data out of the header, if present.

        :param epdb_header: The content of the ``X-EPDB`` header.
        :type epdb_header: string
        :returns: The decoded and decrypt header payload
        :rtype: dictionary
        :raises: EPDBException

        It expects :obj:`epdb_header` to have the ``JWT`` prefix.
        """
        try:
            scheme, payload = epdb_header.split(None, 1)
        except ValueError:
            raise EPDBException('Invalid X-EPDB value; must have two tokens')

        if scheme != 'JWT':
            raise EPDBException('Invalid X-EPDB value; scheme must be JWT')

        return jwt.decode(payload.encode(), self.key, algorithms='HS256')
