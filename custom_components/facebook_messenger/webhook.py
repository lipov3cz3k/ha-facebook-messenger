"""Support for Facebook Messenger Webhooks."""
import logging

from fbmessenger import BaseMessenger
from homeassistant.components.http import HomeAssistantView
from homeassistant.components.notify import ATTR_TARGET
from homeassistant.const import ATTR_COMMAND, HTTP_BAD_REQUEST
from homeassistant.core import callback

from .const import (
    ATTR_ARGS,
    ATTR_MESSAGEID,
    ATTR_TEXT,
    DOMAIN,
    EVENT_FACEBOOK_COMMAND,
    EVENT_FACEBOOK_TEXT,
)

_LOGGER = logging.getLogger(__name__)

FACEBOOK_HANDLER_URL = "/api/facebook_webhooks"


@callback
def async_register_http(hass, page_access_token, verify_token):
    hass.http.register_view(FacebookReceiver(hass, page_access_token, verify_token))


class FacebookReceiver(HomeAssistantView, BaseMessenger):
    """Handle webhooks from Facebook."""

    requires_auth = False
    url = FACEBOOK_HANDLER_URL
    name = "api:facebook_webhooks"

    def __init__(self, hass, page_access_token, verify_token):
        """Initialize the class."""
        super().__init__(page_access_token)
        self.verify_token = verify_token
        self.hass = hass

    async def post(self, request):
        """Accept the POST from Facebook."""
        try:
            data = await request.json()
            _LOGGER.debug("data %s", data)
        except ValueError:
            return self.json_message("Invalid JSON", HTTP_BAD_REQUEST)

        self.handle(data)
        return None

    async def get(self, request):
        """Accept the GET from Facebook."""
        # facebook webhook verification
        if request.query.get("hub.verify_token") == self.verify_token:
            _LOGGER.info("Facebook verification passed")
            return request.query.get("hub.challenge")

        _LOGGER.warning("Unknown GET params")
        return self.json_message("Incorrect secret", HTTP_BAD_REQUEST)

    def _process_text_message(self, text):
        if text[0] == "/":
            pieces = text.split(" ")
            data = {ATTR_COMMAND: pieces[0], ATTR_ARGS: pieces[1:]}
            event = EVENT_FACEBOOK_COMMAND
        else:
            data = {ATTR_TEXT: text}
            event = EVENT_FACEBOOK_TEXT
        return event, data

    def _process_attachments_message(self, attachments):
        pass

    def _process_predefined_commands(self, data):
        if data.get(ATTR_TEXT) == "get my id":
            # refactor to notify event?
            self.send(dict(text=f"Your id is {self.get_user_id()}"))
            return True

        return False

    def message(self, message):
        _LOGGER.info("message %s", message)
        event = None
        event_data = {
            ATTR_TARGET: message.get("sender", {}).get("id"),
            ATTR_MESSAGEID: message["message"].get("mid"),
        }

        if "text" in message["message"]:
            event, data = self._process_text_message(message["message"].get("text"))
            event_data.update(data)

        if "attachments" in message["message"]:
            event, data = self._process_text_message(
                message["message"].get("attachments")
            )

        if self._process_predefined_commands(event_data):
            return

        self.hass.bus.async_fire(event, event_data)
        # might not work due to EU restrictions
        self.send_action("mark_seen")

    def account_linking(self, message):
        _LOGGER.info("account_linking %s", message)

    def delivery(self, message):
        _LOGGER.info("delivery %s", message)

    def optin(self, message):
        _LOGGER.info("optin %s", message)

    def postback(self, message):
        _LOGGER.info("postback %s", message)

    def read(self, message):
        _LOGGER.info("read %s", message)
