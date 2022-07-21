from time import sleep
from typing import Generator

import base.hardware.sbu.serial_interface
import pytest
from base.hardware.sbu.sbu import SBU
from base.hardware.sbu.communicator import SbuCommunicator
from hil_control.hil_control import HilControl
from hil_test.utils.patch_config import patch_config


@pytest.fixture
def sbu() -> Generator[SBU, None, None]:
    patch_config(base.hardware.sbu.serial_interface.SerialInterface, {  "wait_for_channel_free_timeout": 2,
  "sbu_response_timeout": 1,
  "wait_for_measurement_result_timeout": 2,
  "serial_connection_timeout": 1})
    sbu_communicator = SbuCommunicator()
    yield SBU(sbu_communicator)


def test_shutdown(sbu: SBU) -> None:
    hil_control = HilControl()
    sbu.request_shutdown()
    assert hil_control.bcu_supply_present()
    hil_control.deactivate_3v3()
    sleep(0.1)
    assert not hil_control.bcu_supply_present()
