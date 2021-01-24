"""Facebook Messenger for notify component."""
import logging

from fbmessenger import MessengerClient
from homeassistant.components.notify import (
    ATTR_TARGET,
    ATTR_TITLE,
    PLATFORM_SCHEMA,
    BaseNotificationService,
)
import voluptuous as vol

from .const import ATTR_MESSAGEID, CONF_PAGE_ACCESS_TOKEN, EVENT_FACEBOOK_SENT

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Required(CONF_PAGE_ACCESS_TOKEN): vol.Coerce(str)}
)


def get_service(hass, config, discovery_info=None):
    """Get the Facebook Messenger notification service."""
    page_access_token = config.get(CONF_PAGE_ACCESS_TOKEN)
    return FacebookMessengerNotificationService(hass, page_access_token)


class FacebookMessengerNotificationService(BaseNotificationService):
    def __init__(self, hass, page_access_token):
        """Initialize the service."""
        self.hass = hass
        self.client = MessengerClient(page_access_token)

    def send_message(self, message="", **kwargs):
        """Send a message to a user."""
        targets = kwargs.get(ATTR_TARGET)

        # text message
        title = kwargs.get(ATTR_TITLE)
        payload = dict(text=f"{title}\n{message}" if title else message)

        _LOGGER.debug("Send message to %s, with payload %s ", targets, payload)
        for target in targets:
            try:
                out = self.client.send(
                    payload, target, messaging_type="MESSAGE_TAG", tag="ACCOUNT_UPDATE"
                )
                _LOGGER.debug(out)

                event_data = {
                    ATTR_TARGET: out.get("recipient_id"),
                    ATTR_MESSAGEID: out.get("message_id"),
                }
                self.hass.bus.async_fire(EVENT_FACEBOOK_SENT, event_data)
            except ValueError as exc:
                _LOGGER.error(exc)
