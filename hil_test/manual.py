import RPi.GPIO as GPIO
from time import sleep

from base.hardware.pin_interface import PinInterface

PIN_IN_5V = 3
PIN_OUT_3V3 = 5

pin_interface = PinInterface.global_instance()


def setup_for_hil_tests():
    GPIO.setup(PIN_IN_5V, GPIO.IN)
    GPIO.setup(PIN_OUT_3V3, GPIO.OUT)


def hil_test_3v3_readout():
    try:
        while True:
            GPIO.output(PIN_OUT_3V3, GPIO.HIGH)
            sleep(1)
            GPIO.output(PIN_OUT_3V3, GPIO.LOW)
            sleep(1)
    except KeyboardInterrupt:
        print("Exit")
    GPIO.output(PIN_OUT_3V3, GPIO.LOW)


def hil_test_sleep_wakeup():
    ...


def hil_test_5v_switchoff_after_3v3_low():
    GPIO.output(PIN_OUT_3V3, GPIO.HIGH)
    input("Testing switchoff 5v after 3,3 is low. Press enter ...")
    GPIO.output(PIN_OUT_3V3, GPIO.LOW)
    sleep(1)
    assert not GPIO.input(PIN_IN_5V)


if __name__ == "__main__":
    setup_for_hil_tests()
    # hil_test_3v3_readout()
    hil_test_sleep_wakeup()

GPIO.cleanup()
