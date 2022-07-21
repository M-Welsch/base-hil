import RPi.GPIO as GPIO
from base.hardware.pin_interface import PinInterface


PIN_IN_5V = 3
PIN_OUT_3V3 = 5


class HilControl:
    def __init__(self):
        self._pin_interface = PinInterface.global_instance()
        self._setup_for_hil_tests()

    @staticmethod
    def _setup_for_hil_tests():
        GPIO.setup(PIN_IN_5V, GPIO.IN)
        GPIO.setup(PIN_OUT_3V3, GPIO.OUT)

    def deactivate_3v3(self) -> None:
        GPIO.output(PIN_OUT_3V3, GPIO.LOW)

    def activate_3v3(self) -> None:
        GPIO.output(PIN_OUT_3V3, GPIO.HIGH)

    def bcu_supply_present(self) -> bool:
        return GPIO.input(PIN_IN_5V)
