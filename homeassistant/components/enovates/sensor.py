"""Platform for sensor integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .modbusenoone import ModbusEnoOne


@dataclass(frozen=True, kw_only=True)
class EnovatesSensorEntityDescription(SensorEntityDescription):
    """Describes an Envoy Encharge binary sensor entity."""

    value_fn: Callable[[ModbusEnoOne], any]


SENSOR_TYPES: list[EnovatesSensorEntityDescription] = [
    # TODO: add api version
    EnovatesSensorEntityDescription(
        key="number_of_phases",
        translation_key="number_of_phases",
        name="Number of phases",
        value_fn=lambda api: api.get_number_of_phases(),
    ),
    EnovatesSensorEntityDescription(
        key="max_amp_per_phase",
        translation_key="max_amp_per_phase",
        name="Charger hard max current",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=1,
        value_fn=lambda api: api.get_max_amp_per_phase(),
    ),
    # Charger current:
    EnovatesSensorEntityDescription(
        key="charger_current_L1",
        translation_key="charger_current_L1",
        name="Charger current L1",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE,
        suggested_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=1,
        value_fn=lambda api: api.get_charger_current_l1(),
    ),
    EnovatesSensorEntityDescription(
        key="charger_current_L2",
        translation_key="charger_current_L2",
        name="Charger current L2",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE,
        suggested_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=1,
        value_fn=lambda api: api.get_charger_current_l2(),
    ),
    EnovatesSensorEntityDescription(
        key="charger_current_L3",
        translation_key="charger_current_L3",
        name="Charger current L3",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE,
        suggested_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=1,
        value_fn=lambda api: api.get_charger_current_l3(),
    ),
    # Charger voltage:
    EnovatesSensorEntityDescription(
        key="charger_voltage_L1",
        translation_key="charger_voltage_L1",
        name="Charger voltage L1",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=1,
        value_fn=lambda api: api.get_charger_voltage_l1(),
    ),
    EnovatesSensorEntityDescription(
        key="charger_voltage_L2",
        translation_key="charger_voltage_L2",
        name="Charger voltage L2",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=1,
        value_fn=lambda api: api.get_charger_voltage_l2(),
    ),
    EnovatesSensorEntityDescription(
        key="charger_voltage_L3",
        translation_key="charger_voltage_L3",
        name="Charger voltage L3",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=1,
        value_fn=lambda api: api.get_charger_voltage_l3(),
    ),
    # Power:
    EnovatesSensorEntityDescription(
        key="charger_active_power_l1",
        translation_key="charger_active_power_l1",
        name="Charger active power L1",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=1,
        value_fn=lambda api: api.get_charger_active_power_l1(),
    ),
    EnovatesSensorEntityDescription(
        key="charger_active_power_l2",
        translation_key="charger_active_power_l2",
        name="Charger active power L2",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=1,
        value_fn=lambda api: api.get_charger_active_power_l2(),
    ),
    EnovatesSensorEntityDescription(
        key="charger_active_power_l3",
        translation_key="charger_active_power_L3",
        name="Charger active power L3",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=1,
        value_fn=lambda api: api.get_charger_active_power_l3(),
    ),
    EnovatesSensorEntityDescription(
        key="charger_active_power_total",
        translation_key="charger_active_power_total",
        name="Charger active power total",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=1,
        value_fn=lambda api: api.get_charger_active_power_total(),
    ),

    #Installation current
    EnovatesSensorEntityDescription(
        key="installation_current_l1",
        translation_key="installation_current_l1",
        name="Installation current L1",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE,
        suggested_display_precision=1,
        value_fn=lambda api: api.get_installation_current_l1(),
    ),

]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Enovates sensor platform."""
    entities: list[SensorEntity] = []
    api = config_entry.runtime_data["api"]
    entities.extend(EnovatesSensor(api, description) for description in SENSOR_TYPES)
    async_add_entities(entities)


class EnovatesSensor(SensorEntity):
    """Representation of an Enovates binary sensor."""

    _attr_has_entity_name = True
    entity_description: EnovatesSensorEntityDescription

    def __init__(
        self,
        api: ModbusEnoOne,
        description: EnovatesSensorEntityDescription,
    ) -> None:
        """Initialize an EnovatesSensor."""
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
    def native_value(self) -> float | str | None :
        """Return the value reported by the sensor, or None if the relevant sensor can't produce a current measurement."""
        return self.entity_description.value_fn(self._api)
