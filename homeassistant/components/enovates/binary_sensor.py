"""Binary sensors for Enovates integration"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.components.enovates.const import DOMAIN
from homeassistant.components.enovates.modbusenoone import ModbusEnoOne
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback


@dataclass(frozen=True, kw_only=True)
class EnovatesBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes an Envoy Encharge binary sensor entity."""

    value_fn: Callable[[ModbusEnoOne], bool]


SENSOR_TYPES: tuple[EnovatesBinarySensorEntityDescription, ...] = (
    EnovatesBinarySensorEntityDescription(
        key="charging",
        translation_key="charging",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        value_fn=lambda api: api.is_charging,
    ),
    EnovatesBinarySensorEntityDescription(
        key="lock",
        translation_key="lock",
        device_class=BinarySensorDeviceClass.LOCK,
        value_fn=lambda api: api.is_locked,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up envoy binary sensor platform."""
    # coordinator = config_entry.runtime_data
    # envoy_data = coordinator.envoy.data
    # assert envoy_data is not None
    entities: list[BinarySensorEntity] = []
    api = ModbusEnoOne(config_entry.data[CONF_HOST])
    entities.extend(
        EnovatesBinarySensor(api, description) for description in SENSOR_TYPES
    )

    async_add_entities(entities)


class EnovatesBinarySensor(BinarySensorEntity):
    """Representation of an Epion Air sensor."""

    _attr_has_entity_name = True
    entity_description: EnovatesBinarySensorEntityDescription

    def __init__(
        self,
        api: ModbusEnoOne,
        description: EnovatesBinarySensorEntityDescription,
    ) -> None:
        """Initialize an EpionSensor."""
        self._device_id = api.get_serial()
        self.entity_description = description
        self._api = api
        self._attr_unique_id = f"{api.get_serial()}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, api.get_serial())},
            manufacturer="Epion",
            name=api.get_serial(),
            sw_version=api.get_firmware_version(),
            model=api.get_model_number(),
        )

    @property
    def is_on(self) -> bool | None:
        """Return the value reported by the sensor, or None if the relevant sensor can't produce a current measurement."""
        return self.entity_description.value_fn(self._api)

    # @property
    # def device_info(self) -> DeviceInfo:
    #     """Return the device info of this entity's device."""
    #     return DeviceInfo(
    #         identifiers={(DOMAIN, self._device_id)},
    #         name=self._device_name,
    #         manufacturer="Enovates",
    #         model=self._api.get_model_number(),
    #         sw_version=self._api.get_firmware_version(),
    #     )
