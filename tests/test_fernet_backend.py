import json

import pytest
import testfixtures

from falcon_epdb import EPDBException, FernetBackend
from falcon.testing import SimpleTestResource


try:
    # Only run if cryptography is installed
    import cryptography

    @pytest.fixture(autouse=True)
    def fernet_app(fernet_client):
        resource = SimpleTestResource(json={})
        fernet_client.app.add_route('/', resource)
        return fernet_client.app

    def test_fernet_client_activates_epdb_port(fernet, fernet_client, fernet_header, mock_epdb_serve):
        """Test that we start the server."""
        result = fernet_client.simulate_get(headers={
            'X-EPDB': 'Fernet {}'.format(fernet_header)
        })

        assert mock_epdb_serve.called
        assert mock_epdb_serve.called_once_with(port=9000)

    def test_fernet_raises_import_error_if_not_installed(monkeypatch):
        with monkeypatch.context() as context:
            context.delattr('falcon_epdb.fernet')
            with pytest.raises(ImportError):
                FernetBackend('some key')

    def test_fernet_invalid_header_needs_two_tokens(
            fernet_client, fernet_header, mock_epdb_serve):
        """Test that we expect the header to contain a scheme and payload."""

        with testfixtures.LogCapture() as logs:
            result = fernet_client.simulate_get(headers={
                'X-EPDB': '{}'.format(fernet_header)
            })

        result = fernet_client.simulate_get()

        assert result.status_code == 200
        assert not mock_epdb_serve.called
        logs.check_present((
            'falcon_epdb',
            'ERROR',
            'Attempted, but failed, to serve epdb:'
            ' Invalid X-EPDB value; must have two tokens',))


    def test_fernet_invalid_header_needs_correct_scheme(
            fernet_client, fernet_header, mock_epdb_serve):
        """Test that we expect the header to contain the Fernet scheme."""

        with testfixtures.LogCapture() as logs:
            result = fernet_client.simulate_get(headers={
                'X-EPDB': 'Grigio {}'.format(fernet_header)
            })

        result = fernet_client.simulate_get()

        assert result.status_code == 200
        assert not mock_epdb_serve.called
        logs.check_present((
            'falcon_epdb',
            'ERROR',
            'Attempted, but failed, to serve epdb:'
            ' Invalid X-EPDB value; scheme must be Fernet',))

except ImportError:
    pass


