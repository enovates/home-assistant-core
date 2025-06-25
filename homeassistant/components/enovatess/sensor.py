"""Platform for sensor integration."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfElectricCurrent, UnitOfElectricPotential
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from homeassistant.const import CONF_HOST
from .const import DOMAIN, LOGGER
from .dummyenoone import DummyEnoOne
from .modbusenoone import ModbusEnoOne


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Enovates Sensors based on a config entry."""
    # coordinator = entry.runtime_data
    api = ModbusEnoOne(entry.data[CONF_HOST])
    async_add_entities([EnovatesChargerL1Current(api), EnovatesVoltageL1(api)])


class EnovatesChargerL1Current(SensorEntity):
    """Sensor representing the current measured on L1 of the charger."""

    _attr_name = "Charger L1 current"
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_device_class = SensorDeviceClass.CURRENT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2
    _attr_native_value = 0.0

    def __init__(self, eno_one_api: DummyEnoOne) -> None:
        """Construct the Charger L1 Current sensor."""
        super().__init__()
        self._api = eno_one_api
        self._attr_native_value = self._api.get_charger_current_l1()
        self._device_id = "EnoONE1234"
        self._device_name = "EnoONes"

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
            model=self._api.get_model_number(),
            sw_version="1.0.0",
        )

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._attr_native_value = self._api.get_charger_current_l1()


class EnovatesVoltageL1(SensorEntity):
    """Sensor representing the voltage measured on L1 of the charger."""

    _attr_name = "Charger voltage L1"
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2
    _attr_native_value = 0.0

    def __init__(self, eno_one_api: DummyEnoOne) -> None:
        """Construct the Charger L1 Voltage sensor."""
        super().__init__()
        self._api = eno_one_api
        self._attr_native_value = self._api.get_charger_voltage_l1()
        self._device_id = "EnoONE1234"
        self._device_name = "EnoONes"

    @property
    def unique_id(self) -> str | None:
        """Return the unique id of this entity."""
        return "EnovatesVoltage"
        # return f"{self._device_id}_{self._sensor_type}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info of this entity's device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._device_name,
            manufacturer="Enovates",
            model=self._api.get_model_number(),
            sw_version="1.0.0",
        )

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._attr_native_value = self._api.get_charger_voltage_l1()
