"""Support for Tesla sliders (by using lights)."""
import logging

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    SUPPORT_BRIGHTNESS,
    LightEntity,
)

from . import DOMAIN as TESLA_DOMAIN, TeslaDevice

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Tesla sliders by config_entry."""
    controller = hass.data[TESLA_DOMAIN][config_entry.entry_id]["controller"]
    entities = []
    for device in hass.data[TESLA_DOMAIN][config_entry.entry_id]["devices"]["light"]:
        if device.type == "chargelimit slider":
            entities.append(ChargerLimitSlider(device, controller, config_entry))
    async_add_entities(entities, True)


class ChargerLimitSlider(TeslaDevice, LightEntity):
    """Representation of a Tesla chargelimit slider."""

    def __init__(self, tesla_device, controller, config_entry):
        """Initialize the Tesla device."""
        super().__init__(tesla_device, controller, config_entry)
        self._chargelimit_soc = None

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_BRIGHTNESS

    async def async_update(self):
        """Call by the Tesla device callback to update state."""
        _LOGGER.debug("Updating: %s", self._name)
        await super().async_update()
        self._chargelimit_soc = self.tesla_device.get_charge_limit_soc()
        _LOGGER.debug("%s: chargelimit_soc is %f", self._name, self._chargelimit_soc)

    @property
    def brightness(self):
        """Return the 'brightness', which is the chargelimit soc."""
        """0-100% -> 0-255"""
        return int(round((self._chargelimit_soc / 100.0) * 255))

    @property
    def is_on(self):
        """Return the light state (which is silly and always on for us)."""
        return True

    async def async_turn_on(self, **kwargs):
        """Turn device on (aka set chargelimit soc)."""
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        if brightness:
            """ 0-255 -> 0-100% """
            soc = int(round((brightness / 255.0) * 100))
            _LOGGER.debug("%s: Setting chargelimit soc to %s%%", self._name, soc)
            await self.tesla_device.set_charge_limit_soc(soc)

    async def async_turn_off(self, **kwargs):
        """Turn device off (which is silly and not supported)."""
        raise Exception("You can't turn off your charge limit, silly ;-)")
