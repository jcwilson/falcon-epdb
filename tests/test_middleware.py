"""Tests for the core middleware functionality"""

import base64
import json

import pytest
import testfixtures


def test_options_call(base64_client, base64_header, mock_epdb_serve):
    """Test that we do not start the server on an OPTIONS call."""
    result = base64_client.simulate_options(headers={"X-EPDB": "Base64 {}".format(base64_header)})

    assert result.status_code == 200
    assert not mock_epdb_serve.called


def test_header_exception_is_not_fatal(base64_client, mock_epdb_serve):
    """Test that we do not fail the request if the header processing fails."""
    with testfixtures.LogCapture() as logs:
        result = base64_client.simulate_get(headers={"X-EPDB": "Invalid"})

    assert result.status_code == 200
    assert not mock_epdb_serve.called
    logs.check_present(
        (
            "falcon_epdb",
            "ERROR",
            "Attempted, but failed, to serve epdb: Invalid X-EPDB value; must have two tokens",
        )
    )


def test_unexpected_header_exception_is_not_fatal(base64_client, base64_middleware, mocker):
    """We should not fail the request if the header processing fails in an unexpected manner."""

    mocker.patch.object(
        base64_middleware.backend, "get_header_data", side_effect=RuntimeError("Oops")
    )

    with testfixtures.LogCapture() as logs:
        result = base64_client.simulate_get(headers={"X-EPDB": "Invalid"})

    assert result.status_code == 200
    logs.check_present(
        (
            "falcon_epdb",
            "ERROR",
            "Attempted, but failed, to serve epdb:"
            " Unexpected error when processing the X-EPDB header",
        )
    )


def test_epdb_serve_exception_is_not_fatal(base64_client, base64_header, mock_epdb_serve):
    """Test that we do not fail the request if the epdb.serve() call fails."""
    mock_epdb_serve.configure_mock(side_effect=RuntimeError("Oops"))

    with testfixtures.LogCapture() as logs:
        result = base64_client.simulate_get(headers={"X-EPDB": "Base64 {}".format(base64_header)})

    assert result.status_code == 200
    assert mock_epdb_serve.called
    logs.check_present(
        (
            "falcon_epdb",
            "ERROR",
            "Attempted, but failed, to serve epdb: Unexpected error when starting epdb server",
        )
    )


def test_no_header_has_no_effect(base64_client, mock_epdb_serve):
    """Test that we do nothing if the header is not present."""
    result = base64_client.simulate_get()

    assert result.status_code == 200
    assert not mock_epdb_serve.called


@pytest.mark.parametrize(
    "header_data, error_msg",
    (
        pytest.param(["epdb", {}], "Invalid X-EPDB content; must be a dictionary", id="not-a-dict"),
        pytest.param(
            {"not_epdb": {}}, 'Invalid X-EPDB content; must contain key named "epdb"', id="no-epdb"
        ),
        pytest.param(
            {"epdb": "not a dict"},
            'Invalid X-EPDB content; "epdb" key must map to a dictionary',
            id="no-dict",
        ),
    ),
)
def test_invalid_header_value_content(base64_client, mock_epdb_serve, header_data, error_msg):
    """Test that we expect the header data to contain the "epdb" key."""
    base64_header = base64.b64encode(json.dumps(header_data).encode()).decode()

    with testfixtures.LogCapture() as logs:
        result = base64_client.simulate_get(headers={"X-EPDB": "Base64 {}".format(base64_header)})

    result = base64_client.simulate_get()

    assert result.status_code == 200
    assert not mock_epdb_serve.called
    logs.check_present(
        ("falcon_epdb", "ERROR", "Attempted, but failed, to serve epdb: {}".format(error_msg))
    )
