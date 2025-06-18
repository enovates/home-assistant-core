"""Platform for sensor integration."""

from __future__ import annotations

import logging
import random

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfElectricCurrent, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN
from .enoone import EnoOne

_LOG = logging.getLogger("enovates")


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""

    eno_one_api = EnoOne()

    add_entities(
        [
            EnovatesChargerL1Current(eno_one_api),
            EnovatesChargerL2Current(eno_one_api),
            EnovatesChargerL3Current(eno_one_api),
            EnovatesChargerTotalActivePowerSensor(eno_one_api),
        ]
    )


class EnovatesChargerTotalActivePowerSensor(SensorEntity):
    """Representation the Enovates EnoOne L1 total active power."""

    _attr_name = "Charger total active power"
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2

    def __init__(self, eno_one_api: EnoOne) -> None:
        """Construct the EnovatesChargerTotalActivePowerSensor."""
        super().__init__()
        self._api = eno_one_api
        self._attr_native_value = self._api.get_charger_L1_current()  # this is wrong!
        self._device_id = "EnoONE123"
        self._device_name = "EnoONe"

    @property
    def unique_id(self) -> str | None:
        """Return the entity unique id."""
        return "EnovatesChargerTotalActivePowerSensor"
        # return f"{self._device_id}_{self._sensor_type}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info of this entity's device."""
        _LOG.warning("77777777777777 ---- here device info")
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._device_name,
            manufacturer="Enovates",
            model="Device Model",
            sw_version="1.0.0",
        )

    def update(self) -> None:
        """Update the state of this entity."""
        _LOG.warning("77777777777777 ---- here update")
        self._attr_native_value = self._api.get_charger_L1_current()


class EnovatesChargerL1Current(SensorEntity):
    """Sensor representing the current measured on L1 of the charger."""

    _attr_name = "Charger L1 current"
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2
    _attr_native_value = 0.0

    def __init__(self, eno_one_api: EnoOne) -> None:
        """Construct the Charger L1 Current sensor."""
        super().__init__()
        self._api = eno_one_api
        self._attr_native_value = self._api.get_charger_L1_current()
        self._device_id = "EnoONE123"
        self._device_name = "EnoONe"

    @property
    def unique_id(self) -> str | None:
        """Return the unique id of this entity."""
        return "EnovatesChargerL1Current"
        # return f"{self._device_id}_{self._sensor_type}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info of this entity's device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._device_name,
            manufacturer="Enovates",
            model="Device Model",
            sw_version="1.0.0",
        )

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._attr_native_value = random.uniform(10, 11)


class EnovatesChargerL2Current(SensorEntity):
    """Sensor representing the current measured on L2 of the charger."""

    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2
    _attr_native_value = 0.0

    def __init__(self, eno_one_api: EnoOne) -> None:
        """Construct the Charger L2 Current sensor."""
        super().__init__()
        self._device_id = "EnoONE123"
        self._device_name = "EnoONe"
        self._api = eno_one_api
        self._attr_native_value = self._api.get_charger_L2_current()

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info of the device associated with this entity."""

        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._device_name,
            manufacturer="Enovates",
            model="Device Model",
            sw_version="1.0.0",
        )

    @property
    def name(self) -> str:
        """Return the name of this entity."""
        return "Charger L2 current"
        # return f"My Device {self._sensor_type}"

    @property
    def unique_id(self) -> str | None:
        """Return the unique id of this entity."""
        return "EnovatesChargerL2Current"
        # return f"{self._device_id}_{self._sensor_type}"

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._attr_native_value = random.uniform(10, 11)


class EnovatesChargerL3Current(SensorEntity):
    """Sensor representing the current measured on L3 of the charger."""

    _attr_name = "Charger L3 current"
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2
    _attr_native_value = 0.0

    def __init__(self, eno_one_api: EnoOne) -> None:
        """Construct the Charger L3 Current sensor."""
        super().__init__()
        self._device_id = "EnoONE123"
        self._device_name = "EnoONe"
        self._api = eno_one_api
        self._attr_native_value = self._api.get_charger_L3_current()

    @property
    def unique_id(self) -> str | None:
        """Return the unique id of this entity."""
        return "EnovatesChargerL3Current"
        # return f"{self._device_id}_{self._sensor_type}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info of the device associated with this entity."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._device_name,
            manufacturer="Enovates",
            model="Device Model",
            sw_version="1.0.0",
        )

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._attr_native_value = random.uniform(10, 11)
