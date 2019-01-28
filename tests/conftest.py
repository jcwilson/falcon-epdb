import pytest
import falcon
from falcon.testing import TestClient

from falcon_epdb import EPDBServe, FernetBackend, JWTBackend

try:
    from cryptography.fernet import Fernet
except ImportError:
    pass

@pytest.fixture
def mock_epdb_serve(mocker):
    return mocker.patch('falcon_epdb.epdb.serve')


@pytest.fixture
def fernet_key():
    return b'mVk0ZaJdN2akNwLRpxmuuUOTLgB75n5kxB6KZvDwEWo='


@pytest.fixture
def fernet(fernet_key):
    return Fernet(key=fernet_key)


@pytest.fixture
def fernet_client(fernet_key):
    epdb_serve = EPDBServe(
        backend=FernetBackend(key=fernet_key),
        serve_options={'port': 9000})
    return TestClient(falcon.API(middleware=[epdb_serve]))


@pytest.fixture
def jwt_key():
    return 'mVk0ZaJdN2akNwLRpxmuuUOTLgB75n5kxB6KZvDwEWo='


@pytest.fixture
def jwt_client(jwt_key):
    epdb_serve = EPDBServe(
        backend=JWTBackend(key=jwt_key),
        serve_options={'port': 9000})
    return TestClient(falcon.API(middleware=[epdb_serve]))
