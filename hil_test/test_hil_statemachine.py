from datetime import datetime, timedelta

import pytest
import hil_control.hw_rev4_pcu_interface as pcu


@pytest.mark.hardware_in_the_loop
def test_hil_shutdown_init():
    init_outputs = pcu.cmd.shutdown.init()
    deep_sleep_outputs = pcu.check_messages(6)
    wakeup_outputs = pcu.debugcmd.wakeup()
    wakeup_reason = pcu.get_wakeup_reason()
    assert any(['shutdown_requested state' in init_output for init_output in init_outputs]), f"see {' '.join(init_outputs)}"
    assert any(['deep_sleep state' in deep_sleep_output for deep_sleep_output in deep_sleep_outputs]), f"see {' '.join(deep_sleep_outputs)}"
    assert any(['active state' in wakeup_output for wakeup_output in wakeup_outputs]), f"see {' '.join(wakeup_outputs)}"
    assert wakeup_reason == pcu.WakeupReason.WAKEUP_REASON_USER_REQUEST


@pytest.mark.hardware_in_the_loop
def test_hil_shutdown_init_and_abort():
    init_outputs = pcu.cmd.shutdown.init()
    abort_outputs = pcu.cmd.shutdown.abort()
    assert any(['shutdown_requested state' in init_output for init_output in init_outputs]), f"see {' '.join(init_outputs)}"
    assert any(['active state' in abort_output for abort_output in abort_outputs]), f"see {' '.join(abort_outputs)}"


@pytest.mark.hardware_in_the_loop
def test_hil_shutdown_init_with_scheduled_wakeup():
    now = datetime.now()
    later = datetime.now() + timedelta(minutes=1)
    pcu._set_date(pcu.DateKind.now, now)
    pcu._set_date(pcu.DateKind.wakeup, later)
    init_outputs = pcu.cmd_shutdown_init()
    deep_sleep_outputs = pcu.check_messages(6)
    assert any(
        ['shutdown_requested state' in init_output for init_output in init_outputs]), f"see {' '.join(init_outputs)}"
    assert any(['deep_sleep state' in deep_sleep_output for deep_sleep_output in
                deep_sleep_outputs]), f"see {' '.join(deep_sleep_outputs)}"

    wakeup_outputs = pcu.check_messages(120)
    assert any(['active state' in wakeup_output for wakeup_output in wakeup_outputs]), f"see {' '.join(wakeup_outputs)}"
    wakeup_reason = pcu.get_wakeup_reason()
    assert wakeup_reason == pcu.WakeupReason.WAKEUP_REASON_SCHEDULED


@pytest.mark.hardware_in_the_loop
def test_hil_shutdown_with_wakeup_into_hmi():
    pcu.cmd.shutdown.init()
    pcu.debugcmd.button_pressed(0)
    # should be in hmi state now
    pcu.debugcmd.wakeup()
    # assert active state

