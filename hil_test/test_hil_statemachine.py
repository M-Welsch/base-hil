import pytest
import hil_control.hw_rev4_pcu_interface as pcu


def test_hil_shutdown_init_and_abort():
    init_outputs = pcu.cmd_shutdown_init()
    abort_outputs = pcu.cmd_shutdown_abort()
    assert any(['shutdown_requested state' in init_output for init_output in init_outputs]), f"see {' '.join(init_outputs)}"
    assert any(['active state' in abort_output for abort_output in abort_outputs]), f"see {' '.join(abort_outputs)}"
