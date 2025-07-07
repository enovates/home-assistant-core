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
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=1,
        value_fn=lambda api: api.get_charger_current_l1(),
    ),
    EnovatesSensorEntityDescription(
        key="charger_current_L2",
        translation_key="charger_current_L2",
        name="Charger current L2",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=1,
        value_fn=lambda api: api.get_charger_current_l2(),
    ),
    EnovatesSensorEntityDescription(
        key="charger_current_L3",
        translation_key="charger_current_L3",
        name="Charger current L3",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
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
    # Installation current
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
    # coordinator = config_entry.runtime_data
    # envoy_data = coordinator.envoy.data
    # assert envoy_data is not None
    entities: list[SensorEntity] = []
    api = ModbusEnoOne(config_entry.data[CONF_HOST])
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
    def native_value(self) -> any:
        """Return the value reported by the sensor, or None if the relevant sensor can't produce a current measurement."""
        return self.entity_description.value_fn(self._api)


# class EnovatesChargerL1Current(SensorEntity):
#     """Sensor representing the current measured on L1 of the charger."""

#     _attr_name = "Charger L1 current"
#     _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
#     _attr_device_class = SensorDeviceClass.CURRENT
#     _attr_state_class = SensorStateClass.MEASUREMENT
#     _attr_suggested_display_precision = 2

#     def __init__(self, eno_one_api: ModbusEnoOne) -> None:
#         """Construct the Charger L1 Current sensor."""
#         super().__init__()
#         self._api = eno_one_api
#         self._device_id = self._api.get_serial()
#         self._device_name = self._api.get_serial()

#     @property
#     def unique_id(self) -> str | None:
#         """Return the unique id of this entity."""
#         return f"{self._device_id}_Current_L1"
#         # return f"{self._device_id}_{self._sensor_type}"

#     @property
#     def device_info(self) -> DeviceInfo:
#         """Return the device info of this entity's device."""
#         return DeviceInfo(
#             identifiers={(DOMAIN, self._device_id)},
#             name=self._api.get_serial(),
#             manufacturer="Enovates",
#             model=self._api.get_model_number(),  # TODO: probably a bad idea to fetch this every time
#             sw_version=self._api.get_firmware_version(),
#         )

#     def update(self) -> None:
#         """Fetch new state data for the sensor.

#         This is the only method that should fetch new data for Home Assistant.
#         """
#         self._attr_native_value = self._api.get_charger_current_l1() / 1000.0


# class EnovatesVoltageL1(SensorEntity):
#     """Sensor representing the voltage measured on L1 of the charger."""

#     _attr_name = "Charger voltage L1"
#     _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
#     _attr_device_class = SensorDeviceClass.VOLTAGE
#     _attr_state_class = SensorStateClass.MEASUREMENT
#     _attr_suggested_display_precision = 2

#     def __init__(self, eno_one_api: ModbusEnoOne) -> None:
#         """Construct the Charger L1 Voltage sensor."""
#         super().__init__()
#         self._api = eno_one_api
#         self._device_id = self._api.get_serial()
#         self._device_name = self._api.get_serial()

#     @property
#     def unique_id(self) -> str | None:
#         """Return the unique id of this entity."""
#         return f"{self._device_id}_VoltageL1"

#     @property
#     def device_info(self) -> DeviceInfo:
#         """Return the device info of this entity's device."""
#         return DeviceInfo(
#             identifiers={(DOMAIN, self._device_id)},
#             name=self._device_name,
#             manufacturer="Enovates",
#             model=self._api.get_model_number(),
#             sw_version=self._api.get_firmware_version(),
#         )

#     def update(self) -> None:
#         """Fetch new state data for the sensor.

#         This is the only method that should fetch new data for Home Assistant.
#         """
#         self._attr_native_value = self._api.get_charger_voltage_l1()
