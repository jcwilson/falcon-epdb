"""Fixtures for falcon_epdb tests."""

import base64
import json
import pytest
import falcon
from falcon.testing import TestClient, SimpleTestResource

from falcon_epdb import EPDBServe, Base64Backend, FernetBackend, JWTBackend

try:
    from cryptography.fernet import Fernet
except ImportError:
    pass

try:
    import jwt
except ImportError:
    pass


@pytest.fixture
def mock_epdb_serve(mocker):
    """Mock the epdb.serve() method."""
    return mocker.patch("falcon_epdb.epdb.serve")


@pytest.fixture
def base64_header():
    """Provide the Base64 header value string."""
    return base64.b64encode(json.dumps({"epdb": {}}).encode()).decode()


@pytest.fixture
def base64_middleware():
    """Provide a middleware configured with the Base64Backend."""
    return EPDBServe(backend=Base64Backend(), serve_options={"port": 9000})


@pytest.fixture
def base64_app(base64_middleware):
    """Provide an app configured with the Base64 middleware."""
    app = falcon.API(middleware=[base64_middleware])
    app.add_route("/", SimpleTestResource(json={}))
    return app


@pytest.fixture
def base64_client(base64_app):
    """Provide a client to call the Base64 backend app."""
    return TestClient(base64_app)


@pytest.fixture
def fernet_key():
    """Provide a fernet key value."""
    return b"mVk0ZaJdN2akNwLRpxmuuUOTLgB75n5kxB6KZvDwEWo="


@pytest.fixture
def fernet(fernet_key):
    """Provide a fernet key object."""
    return Fernet(key=fernet_key)


@pytest.fixture
def fernet_header(fernet):
    """Provide the Fernet header value string."""
    return fernet.encrypt(json.dumps({"epdb": {}}).encode()).decode()


@pytest.fixture
def fernet_middleware(fernet_key):
    """Provide a middleware configured with the FernetBackend."""
    return EPDBServe(backend=FernetBackend(key=fernet_key), serve_options={"port": 9000})


@pytest.fixture
def fernet_app(fernet_middleware):
    """Provide an app configured with the Fernet middleware."""
    app = falcon.API(middleware=[fernet_middleware])
    app.add_route("/", SimpleTestResource(json={}))
    return app


@pytest.fixture
def fernet_client(fernet_app):
    """Provide a client to call the Fernet backend app."""
    return TestClient(fernet_app)


@pytest.fixture
def jwt_key():
    """Provide a fernet key value."""
    return "mVk0ZaJdN2akNwLRpxmuuUOTLgB75n5kxB6KZvDwEWo="


@pytest.fixture
def jwt_header(jwt_key):
    """Provide the JWT header value string."""
    return jwt.encode({"epdb": {}}, jwt_key).decode()


@pytest.fixture
def jwt_middleware(jwt_key):
    """Provide a middleware configured with the JWTBackend."""
    return EPDBServe(backend=JWTBackend(key=jwt_key), serve_options={"port": 9000})


@pytest.fixture
def jwt_app(jwt_middleware):
    """Provide an app configured with the JWT middleware."""
    app = falcon.API(middleware=[jwt_middleware])
    app.add_route("/", SimpleTestResource(json={}))
    return app


@pytest.fixture
def jwt_client(jwt_app):
    """Provide a client to call the JWT backend app."""
    return TestClient(jwt_app)
