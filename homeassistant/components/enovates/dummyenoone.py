"""API for the EnoONE chargers."""

import random
import threading


class DummyEnoOne:
    """Implementation of the EnoONE API."""

    def __init__(self) -> None:
        """Construct the EnoONE API."""
        self._charger_L1_current_A = 10
        self._charger_L2_current_A = 10
        self._charger_L3_current_A = 10

        self._l1_voltage_V = 230
        self._l2_voltage_V = 230
        self._l3_voltage_V = 230

        self._update()

    def get_charger_L1_current(self) -> float:
        """Return the actual value of the charger L1 current in amps."""
        return self._charger_L1_current_A

    def get_charger_L2_current(self) -> float:
        """Return the actual value of the charger L2 current in amps."""
        return self._charger_L2_current_A

    def get_charger_L3_current(self) -> float:
        """Return the actual value of the charger L3 current in amps."""
        return self._charger_L3_current_A

    def get_total_active_power(self) -> float:
        """Get the total active power."""
        return self._charger_L1_current_A * self._l1_voltage_V

    def _update(self):
        self._charger_L1_current_A = random.uniform(8, 15)
        self._charger_L2_current_A = random.uniform(8, 15)
        self._charger_L3_current_A = random.uniform(8, 15)

        self.timer = threading.Timer(5.0, self._update)
        self.timer.start()
