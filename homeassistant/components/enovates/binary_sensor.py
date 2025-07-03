"""Binary sensors for Enovates integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN, LOGGER
from .modbusenoone import ModbusEnoOne


@dataclass(frozen=True, kw_only=True)
class EnovatesBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes an Envoy Encharge binary sensor entity."""

    value_fn: Callable[[ModbusEnoOne], bool]


SENSOR_TYPES: list[EnovatesBinarySensorEntityDescription] = [
    EnovatesBinarySensorEntityDescription(
        key="charging",
        translation_key="charging",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        value_fn=lambda api: api.is_charging(),
    ),
    EnovatesBinarySensorEntityDescription(
        key="ev_requesting_power",
        translation_key="ev_requesting_power",
        name="EV requesting power",
        device_class=None,
        value_fn=lambda api: api.is_ev_requesting_power(),
    ),
    EnovatesBinarySensorEntityDescription(
        key="evse_offering_power",
        translation_key="evse_offering_power",
        name="EVSE offering power",
        device_class=None,
        value_fn=lambda api: api.is_evse_offering_power(),
    ),
    EnovatesBinarySensorEntityDescription(
        key="ev_connected",
        translation_key="ev_connected",
        name="EV connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda api: api.is_ev_connected(),
    ),
    EnovatesBinarySensorEntityDescription(
        key="OCPP_Connected",
        translation_key="OCPP_Connected",
        name="OCPP connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda api: api.get_OCPP_state() == 1,
    ),
    EnovatesBinarySensorEntityDescription(
        key="loadshedding_device_connected",
        translation_key="loadshedding_device_connected",
        name="Loadshedding device connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda api: api.get_loadshedding_state() == 1,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Enovates binary sensor platform."""
    # coordinator = config_entry.runtime_data
    # envoy_data = coordinator.envoy.data
    # assert envoy_data is not None
    entities: list[BinarySensorEntity] = []
    api = ModbusEnoOne(config_entry.data[CONF_HOST])
    entities.extend(
        EnovatesBinarySensor(api, description) for description in SENSOR_TYPES
    )
    if api.get_lock_state() != 2:
        LOGGER.warning("777777777 --- charger has lock, adding entity")
        SENSOR_TYPES.append(
            EnovatesBinarySensorEntityDescription(
                key="lock",
                translation_key="lock",
                device_class=BinarySensorDeviceClass.LOCK,
                value_fn=lambda api: api.is_locked(),
            )
        )
        SENSOR_TYPES.append(
            EnovatesBinarySensorEntityDescription(
                key="cable_plugged_in",
                translation_key="cable_plugged_in",
                device_class=BinarySensorDeviceClass.PLUG,
                value_fn=lambda api: api.is_cable_plugged_in(),
            )
        )

    async_add_entities(entities)


class EnovatesBinarySensor(BinarySensorEntity):
    """Representation of an Enovates binary sensor."""

    _attr_has_entity_name = True
    entity_description: EnovatesBinarySensorEntityDescription

    def __init__(
        self,
        api: ModbusEnoOne,
        description: EnovatesBinarySensorEntityDescription,
    ) -> None:
        """Initialize an EnovatesBinarySensor."""
        serial = api.get_serial()
        self._device_id = serial
        self.entity_description = description
        self._api = api
        self._attr_unique_id = f"{serial}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            manufacturer="Enovates",
            name=serial,
            sw_version=api.get_firmware_version(),
            model=api.get_model_number(),
        )

    @property
    def is_on(self) -> bool | None:
        """Return the value reported by the sensor, or None if the relevant sensor can't produce a current measurement."""
        return self.entity_description.value_fn(self._api)
