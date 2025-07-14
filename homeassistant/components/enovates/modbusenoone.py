"""Modbus EnoONE APi."""

import struct

from pymodbus.client import ModbusTcpClient

from .const import LOGGER


class ModbusConnectionError:
    pass


class ModbusEnoOne:
    """Modbus client for Enovates EnoOne charger."""

    def __init__(self, host, port=502, unit_id=1) -> None:
        """Initialize the Modbus client.

        Args:
            host (str): IP address or hostname of the Modbus device
            port (int): Modbus TCP port (default: 502)
            unit_id (int): Modbus unit ID (default: 1)

        """
        self.host = host
        self.port = port
        self.unit_id = unit_id
        self.client = ModbusTcpClient(self.host, port=self.port)
        success = self.client.connect()  # TODO throw exception if connection cannot be made? Different requirements for configflow vs normal startup
        if not success:
            raise ModbusConnectionError

    def _read_holding_register(self, address, data_type="uint16", count=1):
        """Read holding register(s) and convert to specified data type.

        Args:
            address (int): Register address
            data_type (str): Data type (uint16, int16, uint32, int32, string)
            count (int): Number of registers to read

        Returns:
            Converted value or None if error

        """
        # if not self.client or not self.client.is_socket_open():
        #     LOGGER.warning("Modbus client not connected")
        #     self.client.connect()
        #     # TODO re think reconnect logic

        try:
            if data_type in ["uint32", "int32"]:
                # 32-bit values require 2 registers
                result = self.client.read_holding_registers(
                    address, count=2, slave=self.unit_id
                )
            elif data_type == "string":
                # String requires specified count of registers
                result = self.client.read_holding_registers(
                    address, count=count, slave=self.unit_id
                )
            else:
                # 16-bit values require 1 register
                result = self.client.read_holding_registers(
                    address, count=1, slave=self.unit_id
                )

            if result.isError():
                LOGGER.error(f"Error reading register {address}: {result}")
                return None

            # Convert based on data type
            if data_type == "uint16":
                return result.registers[0]
            if data_type == "int16":
                # Convert unsigned to signed
                value = result.registers[0]
                return value if value < 32768 else value - 65536
            if data_type == "uint32":
                # Combine two 16-bit registers (assuming big-endian)
                return (result.registers[0] << 16) | result.registers[1]
            if data_type == "int32":
                # Combine two 16-bit registers and convert to signed
                value = (result.registers[0] << 16) | result.registers[1]
                return value if value < 2147483648 else value - 4294967296
            if data_type == "string":
                # Convert registers to string
                string_bytes = b"".join(
                    struct.pack(">H", reg) for reg in result.registers
                )
                return string_bytes.decode("ascii", errors="ignore").rstrip("\x00")

        except Exception:
            # logger.error(f"Exception reading register {address}: {e}")
            return None

    def get_api_major(self) -> int:
        return self._read_holding_register(0, "uint16")

    def get_api_minor(self) -> int:
        return self._read_holding_register(1, "uint16")

    def get_number_of_phases(self) -> int:
        return self._read_holding_register(50, "uint16")

    def get_max_amp_per_phase(self) -> int:
        return self._read_holding_register(51, "uint16")

    def get_OCPP_state(self) -> int:
        """Get OCPP state.

        1 is accepted, 0 anything else.
        Will also return 1 in case of NO_OCPP.
        """
        return self._read_holding_register(52, "uint16")

    def get_loadshedding_state(self) -> int:
        """Get loadshedding state. Device type None == 0, anything else == 1."""
        return self._read_holding_register(53, "uint16")

    def is_loadshedding_device_connected(self) -> bool:
        """Check if a loadshedding device is connected."""
        ret = self.get_loadshedding_state()
        if ret is None:
            return False
        return ret == 1

    def get_lock_state(self) -> int:
        """Get the lock state. 0 is unlocked, 1 is locked, 2 is 'there is no lock' (i.e. fixed cable)."""
        return self._read_holding_register(54, "uint16")

    def is_locked(self) -> bool:
        lock_state = self.get_lock_state()
        ret = lock_state == 1
        LOGGER.warn(f"7777777 --- {lock_state} {ret}")

    def get_contactor_state(self) -> int:
        return self._read_holding_register(55, "uint16")

    def is_charging(self) -> bool:
        return self.get_contactor_state() == 1

    def get_led_color(self) -> int:
        """Get LED color. (0 off, 1 red, 2 green 3 blue 5 cyan, 5 yellow 6 pinkt 7 white, 8 orange 9 purple)."""
        return self._read_holding_register(56, "uint16")

    # Current sensors (L1, L2, L3)
    def get_charger_current_l1(self) -> int:
        """Get charger current L1 in mA."""
        return self._read_holding_register(200, "uint16")

    def get_charger_current_l2(self) -> int:
        """Get charger current L2 in mA."""
        return self._read_holding_register(201, "uint16")

    def get_charger_current_l3(self) -> int:
        """Get charger current L3 in mA."""
        return self._read_holding_register(202, "uint16")

    # Voltage sensors (L1, L2, L3)
    def get_charger_voltage_l1(self) -> int:
        """Get charger voltage L1 in V."""
        return self._read_holding_register(203, "int16")

    def get_charger_voltage_l2(self) -> int:
        """Get charger voltage L2 in V."""
        return self._read_holding_register(204, "int16")

    def get_charger_voltage_l3(self) -> int:
        """Get charger voltage L3 in V."""
        return self._read_holding_register(205, "int16")

    # Power sensors
    def get_charger_active_power_total(self) -> int:
        """Get charger active power total in W."""
        return self._read_holding_register(206, "uint16")

    def get_charger_active_power_l1(self) -> int:
        """Get charger active power L1 in W."""
        return self._read_holding_register(207, "uint16")

    def get_charger_active_power_l2(self) -> int:
        """Get charger active power L2 in W."""
        return self._read_holding_register(208, "uint16")

    def get_charger_active_power_l3(self) -> int:
        """Get charger active power L3 in W."""
        return self._read_holding_register(209, "uint16")

    # Installation currents (32-bit)
    def get_installation_current_l1(self) -> int:
        """Get installation current L1 in mA."""
        return self._read_holding_register(210, "int32")

    def get_installation_current_l2(self) -> int:
        """Get installation current L2 in mA."""
        return self._read_holding_register(212, "int32")

    def get_installation_current_l3(self) -> int:
        """Get installation current L3 in mA."""
        return self._read_holding_register(214, "int32")

    # Energy
    def get_total_active_energy_import(self) -> int:
        """Get total active energy import in Wh."""
        return self._read_holding_register(216, "uint32")

    # Mode3 state
    def get_mode3_state_as_int(self) -> int:
        return self._read_holding_register(300, "uint16")

    def get_mode3_state(self) -> str:
        """Get Mode3 state as string."""
        return self._read_holding_register(301, "string", 1)

    def is_ev_connected(self) -> bool:
        mode3 = self.get_mode3_state()
        if mode3 is None:
            return None
        return mode3[0] != "A"  # TODO state F

    def is_ev_requesting_power(self) -> bool:
        mode3 = self.get_mode3_state()
        if mode3 is None:
            return None
        return mode3[0] == "C"

    def is_evse_offering_power(self) -> bool:
        pwm = self.get_charger_pwm_as_amp()
        if pwm is None:
            return None
        return pwm > 0

    def is_cable_plugged_in(self) -> bool:
        """Check and return cable connected state.
        Cabled chargers always report plugged_in (true)
        """
        lock_state = self.get_lock_state()
        if lock_state is None:
            return None
        if lock_state == 2:
            return True
        pp = self.get_pp()
        if pp is None:
            return None
        return pp > 0

    # PWM
    def get_charger_pwm_as_amp(self):
        """Get charger PWM as amp in A."""
        return self._read_holding_register(303, "uint16")

    def get_charger_pwm(self):
        """Get charger PWM value."""
        return self._read_holding_register(304, "uint16")

    def get_pp(self):
        return self._read_holding_register(305, "uint16")

    def get_cp_plus(self):
        return self._read_holding_register(306, "uint16")

    def get_cp_min(self):
        return self._read_holding_register(307, "int16")

    # EMS
    def get_ems_applied_softlimit(self) -> int:
        """Get EMS applied softlimit in A."""
        return self._read_holding_register(400, "int16")

    # Token
    def get_last_token(self) -> str | None:
        """Get last scanned token as string."""
        return self._read_holding_register(401, "string", 16)

    def get_manufacturer(self) -> str:
        return self._read_holding_register(5000, "string", 16)

    def get_vendor(self) -> str:
        return self._read_holding_register(5016, "string", 16)

    def get_serial(self) -> str:
        return self._read_holding_register(5032, "string", 16)

    def get_model_number(self) -> str:
        return self._read_holding_register(5048, "string", 16)

    # Firmware
    def get_firmware_version(self) -> str:
        """Get firmware version as string."""
        return self._read_holding_register(5064, "string", 16)


if __name__ == "__main__":
    api = ModbusEnoOne("192.168.30.31")
    try:
        # API Information
        print("=== API Information ===")
        print(f"API Major: {api.get_api_major()}")
        print(f"API Minor: {api.get_api_minor()}")

        # Device Configuration
        print("\n=== Device Configuration ===")
        print(f"Number of phases: {api.get_number_of_phases()}")
        print(f"Max amp per phase: {api.get_max_amp_per_phase()}")

        # Device States
        print("\n=== Device States ===")
        print(f"OCPP state: {api.get_OCPP_state()}")
        print(f"Loadshedding state: {api.get_loadshedding_state()}")
        print(f"Lock state: {api.get_lock_state()}")
        print(f"Contactor state: {api.get_contactor_state()}")
        print(f"LED color: {api.get_led_color()}")

        # Charger Current Measurements
        print("\n=== Charger Current Measurements (mA) ===")
        print(f"Charger current L1: {api.get_charger_current_l1()}")
        print(f"Charger current L2: {api.get_charger_current_l2()}")
        print(f"Charger current L3: {api.get_charger_current_l3()}")

        # Charger Voltage Measurements
        print("\n=== Charger Voltage Measurements (V) ===")
        print(f"Charger voltage L1: {api.get_charger_voltage_l1()}")
        print(f"Charger voltage L2: {api.get_charger_voltage_l2()}")
        print(f"Charger voltage L3: {api.get_charger_voltage_l3()}")

        # Power Measurements
        print("\n=== Power Measurements (W) ===")
        print(f"Charger active power total: {api.get_charger_active_power_total()}")
        print(f"Charger active power L1: {api.get_charger_active_power_l1()}")
        print(f"Charger active power L2: {api.get_charger_active_power_l2()}")
        print(f"Charger active power L3: {api.get_charger_active_power_l3()}")

        # Installation Current Measurements
        print("\n=== Installation Current Measurements (mA) ===")
        print(f"Installation current L1: {api.get_installation_current_l1()}")
        print(f"Installation current L2: {api.get_installation_current_l2()}")
        print(f"Installation current L3: {api.get_installation_current_l3()}")

        # Energy
        print("\n=== Energy ===")
        print(
            f"Total active energy import (Wh): {api.get_total_active_energy_import()}"
        )

        # Mode3 State
        print("\n=== Mode3 State ===")
        print(f"Mode3 state (int): {api.get_mode3_state_as_int()}")
        print(f"Mode3 state (string): {api.get_mode3_state()}")

        # PWM and Control Pilot
        print("\n=== PWM and Control Pilot ===")
        print(f"Charger PWM as amp (A): {api.get_charger_pwm_as_amp()}")
        print(f"Charger PWM: {api.get_charger_pwm()}")
        print(f"PP: {api.get_pp()}")
        print(f"CP+: {api.get_cp_plus()}")
        print(f"CP-: {api.get_cp_min()}")

        # EMS
        print("\n=== EMS ===")
        print(f"EMS applied softlimit (A): {api.get_ems_applied_softlimit()}")

        # Token
        print("\n=== Token ===")
        print(f"Last token: {api.get_last_token()}")

        # Device Information
        print("\n=== Device Information ===")
        print(f"Manufacturer: {api.get_manufacturer()}")
        print(f"Vendor: {api.get_vendor()}")
        print(f"Serial: {api.get_serial()}")
        print(f"Model: {api.get_model_number()}")
        print(f"Firmware: {api.get_firmware_version()}")

    except Exception as e:
        print(f"Error occurred: {e}")
