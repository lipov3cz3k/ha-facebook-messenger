"""Facebook Messenger for notify tests."""

from urllib.parse import urlencode

from homeassistant.core import callback
import pytest
import requests_mock

import custom_components.facebook_messenger.notify as fb


@pytest.fixture
def facebook(hass):
    """Fixture for facebook."""
    access_token = "page-access-token"
    return fb.FacebookMessengerNotificationService(hass, access_token)


async def test_send_simple_message(hass, facebook):
    """Test sending a simple message with success."""

    events = []

    @callback
    def store_event(event):
        """Helepr to store events."""
        events.append(event)

    hass.bus.async_listen(fb.EVENT_FACEBOOK_SENT, store_event)

    with requests_mock.Mocker() as mock:
        mock_uri = (
            f"{facebook.client.graph_url}/me/messages"
            f"?{urlencode(facebook.client.auth_args)}"
        )
        mock.register_uri(
            requests_mock.POST, mock_uri, status_code=200,
        )

        message = "This is just a test"
        target = ["123456"]

        facebook.send_message(message=message, target=target)
        assert mock.called
        assert mock.call_count == 1

        expected_body = {
            "recipient": {"id": target[0]},
            "message": {"text": message},
            "messaging_type": "MESSAGE_TAG",
            "notification_type": "REGULAR",
            "tag": "ACCOUNT_UPDATE",
        }
        assert mock.last_request.json() == expected_body
