"""Modbus EnoONE APi."""

import logging
import struct

from pymodbus.client import ModbusTcpClient

logger = logging.getLogger(__name__)


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
        self.client.connect()

    # def connect(self):
    #     """Connect to the Modbus device."""
    #     try:
    #         self.client = ModbusTcpClient(self.host, port=self.port)
    #         return self.client.connect()
    #     except Exception as e:
    #         logger.error(f"Failed to connect to Modbus device: {e}")
    #         return False

    # def disconnect(self):
    #     """Disconnect from the Modbus device."""
    #     if self.client:
    #         self.client.close()

    def _read_holding_register(self, address, data_type="uint16", count=1):
        """Read holding register(s) and convert to specified data type.

        Args:
            address (int): Register address
            data_type (str): Data type (uint16, int16, uint32, int32, string)
            count (int): Number of registers to read

        Returns:
            Converted value or None if error

        """
        if not self.client or not self.client.is_socket_open():
            logger.error("Modbus client not connected")
            return None

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
                logger.error("Error reading register {address}: {result}")
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

        except Exception as e:
            logger.error(f"Exception reading register {address}: {e}")
            return None

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
    def get_mode3_state(self) -> str:
        """Get Mode3 state as string."""
        return self._read_holding_register(301, "string", 1)

    # PWM
    def get_charger_pwm_as_amp(self):
        """Get charger PWM as amp in A."""
        return self._read_holding_register(303, "uint16")

    def get_charger_pwm(self):
        """Get charger PWM value."""
        return self._read_holding_register(304, "uint16")

    # EMS
    def get_ems_applied_softlimit(self) -> int:
        """Get EMS applied softlimit in A."""
        return self._read_holding_register(400, "int16")

    # Token
    def get_last_token(self) -> str:
        """Get last scanned token as string."""
        return self._read_holding_register(401, "string", 16)

    # Firmware
    def get_firmware_version(self) -> str:
        """Get firmware version as string."""
        return self._read_holding_register(5064, "string", 16)
