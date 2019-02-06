"""Tests for the Base64Backend functionality"""

import pytest
import testfixtures


def test_base64_client_activates_epdb_port(base64_client, base64_header, mock_epdb_serve):
    """Test that we start the server."""
    result = base64_client.simulate_get(headers={"X-EPDB": "Base64 {}".format(base64_header)})

    assert result.status_code == 200
    assert mock_epdb_serve.called
    assert mock_epdb_serve.called_once_with(port=9000)


@pytest.mark.parametrize(
    "header_template, error_msg",
    (
        pytest.param("{}", "Invalid X-EPDB value; must have two tokens", id="too-few-tokens"),
        pytest.param(
            "Base64 {} extra", "Invalid X-EPDB value; must have two tokens", id="too-many-tokens"
        ),
        pytest.param("Base32 {}", "Invalid X-EPDB value; scheme must be Base64", id="need-base64"),
    ),
)
def test_base64_invalid_header_value(
    base64_client, base64_header, mock_epdb_serve, header_template, error_msg
):
    """Test that we expect the header to contain a scheme and payload."""
    with testfixtures.LogCapture() as logs:
        result = base64_client.simulate_get(
            headers={"X-EPDB": header_template.format(base64_header)}
        )

    result = base64_client.simulate_get()

    assert result.status_code == 200
    assert not mock_epdb_serve.called
    logs.check_present(
        ("falcon_epdb", "ERROR", "Attempted, but failed, to serve epdb: {}".format(error_msg))
    )
