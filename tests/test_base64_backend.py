import base64
import json

import testfixtures

from falcon_epdb import EPDBException


def test_base64_client_activates_epdb_port(base64_client, base64_header, mock_epdb_serve):
    """Test that we start the server."""
    result = base64_client.simulate_get(headers={"X-EPDB": "Base64 {}".format(base64_header)})

    assert result.status_code == 200
    assert mock_epdb_serve.called
    assert mock_epdb_serve.called_once_with(port=9000)


def test_options_call(base64_client, base64_header, mock_epdb_serve):
    """Test that we do not start the server on an OPTIONS call."""
    result = base64_client.simulate_options(headers={"X-EPDB": "Base64 {}".format(base64_header)})

    assert result.status_code == 200
    assert not mock_epdb_serve.called


def test_header_exception(base64_client, base64_header, mock_epdb_serve):
    """Test that we do not fail the request if the header processing fails."""
    mock_epdb_serve.configure_mock(side_effect=EPDBException("Oops"))

    with testfixtures.LogCapture() as logs:
        result = base64_client.simulate_get(headers={"X-EPDB": "Base64 {}".format(base64_header)})

    assert result.status_code == 200
    assert mock_epdb_serve.called
    logs.check_present(("falcon_epdb", "ERROR", "Attempted, but failed, to serve epdb: Oops"))


def test_epdb_serve_exception(base64_client, base64_header, mock_epdb_serve):
    """Test that we do not fail the request if the epdb.serve() call fails."""
    mock_epdb_serve.configure_mock(side_effect=RuntimeError("Oops"))

    with testfixtures.LogCapture() as logs:
        result = base64_client.simulate_get(headers={"X-EPDB": "Base64 {}".format(base64_header)})

    assert result.status_code == 200
    assert mock_epdb_serve.called
    logs.check_present(
        ("falcon_epdb", "ERROR", "Unexpected error when processing the X-EPDB header")
    )


def test_no_header_has_no_effect(base64_client, mock_epdb_serve):
    """Test that we do nothing if the header is not present."""
    result = base64_client.simulate_get()

    assert result.status_code == 200
    assert not mock_epdb_serve.called


def test_invalid_header_data_not_a_dict(base64_client, mock_epdb_serve):
    """Test that we expect the header data to be a dict."""
    base64_header = base64.b64encode(json.dumps(["epdb", "not a dict"]).encode()).decode()

    with testfixtures.LogCapture() as logs:
        result = base64_client.simulate_get(headers={"X-EPDB": "Base64 {}".format(base64_header)})

    result = base64_client.simulate_get()

    assert result.status_code == 200
    assert not mock_epdb_serve.called
    logs.check_present(
        (
            "falcon_epdb",
            "ERROR",
            "Attempted, but failed, to serve epdb: Invalid X-EPDB content; must be a dictionary",
        )
    )


def test_invalid_header_data_has_epdb_key(base64_client, mock_epdb_serve):
    """Test that we expect the header data to contain the "epdb" key."""
    base64_header = base64.b64encode(json.dumps({"not_epdb": {}}).encode()).decode()

    with testfixtures.LogCapture() as logs:
        result = base64_client.simulate_get(headers={"X-EPDB": "Base64 {}".format(base64_header)})

    result = base64_client.simulate_get()

    assert result.status_code == 200
    assert not mock_epdb_serve.called
    logs.check_present(
        (
            "falcon_epdb",
            "ERROR",
            "Attempted, but failed, to serve epdb:"
            ' Invalid X-EPDB content; must contain key named "epdb"',
        )
    )


def test_invalid_header_data_has_epdb_dict(base64_client, mock_epdb_serve):
    """Test that we expect the header data to contain the "epdb" key."""
    base64_header = base64.b64encode(json.dumps({"epdb": "not a dict"}).encode()).decode()

    with testfixtures.LogCapture() as logs:
        result = base64_client.simulate_get(headers={"X-EPDB": "Base64 {}".format(base64_header)})

    result = base64_client.simulate_get()

    assert result.status_code == 200
    assert not mock_epdb_serve.called
    logs.check_present(
        (
            "falcon_epdb",
            "ERROR",
            "Attempted, but failed, to serve epdb:"
            ' Invalid X-EPDB content; "epdb" key must map to a dictionary',
        )
    )


def test_base64_invalid_header_needs_two_tokens(base64_client, base64_header, mock_epdb_serve):
    """Test that we expect the header to contain a scheme and payload."""

    with testfixtures.LogCapture() as logs:
        result = base64_client.simulate_get(headers={"X-EPDB": "{}".format(base64_header)})

    result = base64_client.simulate_get()

    assert result.status_code == 200
    assert not mock_epdb_serve.called
    logs.check_present(
        (
            "falcon_epdb",
            "ERROR",
            "Attempted, but failed, to serve epdb: Invalid X-EPDB value; must have two tokens",
        )
    )


def test_base64_invalid_header_needs_correct_scheme(base64_client, base64_header, mock_epdb_serve):
    """Test that we expect the header to contain the Base64 scheme."""

    with testfixtures.LogCapture() as logs:
        result = base64_client.simulate_get(headers={"X-EPDB": "Base32 {}".format(base64_header)})

    result = base64_client.simulate_get()

    assert result.status_code == 200
    assert not mock_epdb_serve.called
    logs.check_present(
        (
            "falcon_epdb",
            "ERROR",
            "Attempted, but failed, to serve epdb: Invalid X-EPDB value; scheme must be Base64",
        )
    )
