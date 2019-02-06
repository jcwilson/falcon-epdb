"""Tests for the JWTBackend functionality"""

import pytest
import testfixtures

from falcon_epdb import JWTBackend


try:
    # Only run if pyjwt is installed
    import jwt  # NoQA  # pylint: disable=unused-import

    def test_jwt_client_activates_epdb_port(jwt_client, jwt_header, mock_epdb_serve):
        """Test that we start the server when an appropriate header is received."""

        result = jwt_client.simulate_get(headers={"X-EPDB": "JWT {}".format(jwt_header)})

        assert result.status_code == 200
        assert mock_epdb_serve.called
        assert mock_epdb_serve.called_once_with(port=9000)

    def test_jwt_raises_import_error_if_not_installed(monkeypatch):
        """Expect an import error if we attempt to use this backend without jwt."""

        with monkeypatch.context() as context:
            context.delattr("falcon_epdb.jwt")
            with pytest.raises(ImportError):
                JWTBackend("some key")

    def test_jwt_invalid_header_needs_two_tokens(jwt_client, jwt_header, mock_epdb_serve):
        """Test that we expect the header to contain a scheme and payload."""
        with testfixtures.LogCapture() as logs:
            result = jwt_client.simulate_get(headers={"X-EPDB": "{}".format(jwt_header)})

        result = jwt_client.simulate_get()

        assert result.status_code == 200
        assert not mock_epdb_serve.called
        logs.check_present(
            (
                "falcon_epdb",
                "ERROR",
                "Attempted, but failed, to serve epdb: Invalid X-EPDB value; must have two tokens",
            )
        )

    def test_jwt_invalid_header_needs_correct_scheme(jwt_client, jwt_header, mock_epdb_serve):
        """Test that we expect the header to contain the JWT scheme."""
        with testfixtures.LogCapture() as logs:
            result = jwt_client.simulate_get(headers={"X-EPDB": "Bearer {}".format(jwt_header)})

        result = jwt_client.simulate_get()

        assert result.status_code == 200
        assert not mock_epdb_serve.called
        logs.check_present(
            (
                "falcon_epdb",
                "ERROR",
                "Attempted, but failed, to serve epdb: Invalid X-EPDB value; scheme must be JWT",
            )
        )


except ImportError:
    pass
