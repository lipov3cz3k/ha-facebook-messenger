""" Facebook Messenger Integration """
import logging

from homeassistant import core
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import CONF_PAGE_ACCESS_TOKEN, CONF_VERIFY_TOKEN, DOMAIN
from .webhook import async_register_http

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_PAGE_ACCESS_TOKEN): cv.string,
                vol.Required(CONF_VERIFY_TOKEN): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the Facebook Messenger Custom component."""
    if not config[DOMAIN]:
        _LOGGER.error("Missing config")
        return False

    config = config[DOMAIN]
    async_register_http(hass, config[CONF_PAGE_ACCESS_TOKEN], config[CONF_VERIFY_TOKEN])
    _LOGGER.debug("Async setup done")
    return True
