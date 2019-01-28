import pytest

from falcon_epdb import __version__


@pytest.fixture
def mock_epdb_serve(mocker):
    return mocker.patch('falcon_epdb.epdb.serve')


def test_version():
    assert __version__ == '0.1.0'

def test_mocked_epdb_serve(mock_epdb_serve):
    assert False
