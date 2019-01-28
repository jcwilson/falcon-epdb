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
    """ Raised when an error occurs during the processing of an X-EPDB header. """

class EPDBServe(object):
    """ A middleware to enable remote debuging via an epdb server.

        A client may include a special X-EPDB header containing a JWT payload signed with a
        pre-shared secret key. If this header is present and can be decoded, this middleware will
        begin listening for an epdb client connection, in a blocking manner. At this point, one can
        connect to the epdb server from a remote client and begin interactive debugging of the
        request.

        A well-formed header has JWT-decoded content simply of the form::

            {
                "epdb": {}
            }

        and is encoded with the pre-shared secret key and the default ``HS-256`` algorithm.

    """
    def __init__(self, backend, exempt_methods=('OPTIONS',), serve_options=None):
        serve_options = serve_options or {}
        self.backend = backend
        self.exempt_methods = exempt_methods
        self.serve_options = serve_options

    def process_request(self, req, resp):
        """Check for a well-formed X-EPDB header and if present enable the epdb server."""
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
    __metaclass__ = ABCMeta

    @abstractmethod
    def decode_header_value(self, value):
        pass

    def get_header_data(self, req):
        epdb_header = req.headers.get('X-EPDB')
        if epdb_header:
            logger.debug('Found epdb header')
            header_value = self.decode_header_value(epdb_header)
            return self.validate_header_value(header_value)

    def validate_header_value(self, value):
        if not isinstance(value, dict):
            raise ValueError('Invalid X-EPDB value; must be a dictionary')

        if 'epdb' not in value:
            raise ValueError('Invalid X-EPDB value; must contain key named "epdb"')

        if not isinstance(value['epdb'], dict):
            raise ValueError('Invalid X-EPDB value; "epdb" key must map to a dictionary')

        return value['epdb']


class FernetBackend(EPDBBackend):

    def __init__(self, key):
        try:
            self.fernet = fernet.Fernet(key)
        except NameError:
            raise ImportError('Missing optional [fernet] dependency')

    def decode_header_value(self, epdb_header):
        try:
            scheme, payload = epdb_header.split(None, 1)
        except ValueError:
            raise ValueError('Invalid X-EPDB value; must have two tokens')

        if scheme != 'Fernet':
            raise ValueError('Invalid X-EPDB value; scheme must be Fernet')

        decrypted_bytes = self.fernet.decrypt(payload.encode())
        decrypted_string = decrypted_bytes.decode()
        return json.loads(decrypted_string)


class JWTBackend(EPDBBackend):

    def __init__(self, key):
        try:
            jwt
        except NameError:
            raise ImportError('Missing optional [jwt] dependency')

        self.key = key

    def decode_header_value(self, epdb_header):
        try:
            scheme, payload = epdb_header.split(None, 1)
        except ValueError:
            raise ValueError('Invalid X-EPDB value; must have two tokens')

        if scheme != 'JWT':
            raise ValueError('Invalid X-EPDB value; scheme must be JWT')

        return jwt.decode(payload.encode(), self.key, algorithms='HS256')
