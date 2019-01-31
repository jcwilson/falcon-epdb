import json

import pytest
import testfixtures

from falcon_epdb import EPDBException, JWTBackend
from falcon.testing import SimpleTestResource


try:
    # Only run if pyjwt is installed
    import jwt

    @pytest.fixture(autouse=True)
    def jwt_app(jwt_client):
        resource = SimpleTestResource(json={})
        jwt_client.app.add_route('/', resource)
        return jwt_client.app

    def test_jwt_client(jwt_key, jwt_client, jwt_header, mock_epdb_serve):
        """Test that we start the server."""
        result = jwt_client.simulate_get(headers={
            'X-EPDB': 'JWT {}'.format(jwt_header)
        })

        assert mock_epdb_serve.called
        assert mock_epdb_serve.called_once_with(port=9000)

    def test_jwt_raises_import_error_if_not_installed(monkeypatch):
        with monkeypatch.context() as context:
            context.delattr('falcon_epdb.jwt')
            with pytest.raises(ImportError):
                JWTBackend('some key')

    def test_jwt_invalid_header_needs_two_tokens(
            jwt_client, jwt_header, mock_epdb_serve):
        """Test that we expect the header to contain a scheme and payload."""

        with testfixtures.LogCapture() as logs:
            result = jwt_client.simulate_get(headers={
                'X-EPDB': '{}'.format(jwt_header)
            })

        result = jwt_client.simulate_get()

        assert result.status_code == 200
        assert not mock_epdb_serve.called
        logs.check_present((
            'falcon_epdb',
            'ERROR',
            'Attempted, but failed, to serve epdb:'
            ' Invalid X-EPDB value; must have two tokens',))

    def test_jwt_invalid_header_needs_correct_scheme(
            jwt_client, jwt_header, mock_epdb_serve):
        """Test that we expect the header to contain the JWT scheme."""

        with testfixtures.LogCapture() as logs:
            result = jwt_client.simulate_get(headers={
                'X-EPDB': 'Grigio {}'.format(jwt_header)
            })

        result = jwt_client.simulate_get()

        assert result.status_code == 200
        assert not mock_epdb_serve.called
        logs.check_present((
            'falcon_epdb',
            'ERROR',
            'Attempted, but failed, to serve epdb:'
            ' Invalid X-EPDB value; scheme must be JWT',))

except ImportError:
    pass


