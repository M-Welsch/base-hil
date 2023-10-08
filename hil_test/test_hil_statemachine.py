from datetime import datetime, timedelta

import pytest
import hil_control.hw_rev4_pcu_interface as pcu


@pytest.mark.hardware_in_the_loop
@pytest.mark.asyncio
async def test_hil_shutdown_init():
    init_outputs = await pcu.cmd.shutdown.init()
    deep_sleep_outputs = await pcu.check_messages(6)
    wakeup_outputs = await pcu.debugcmd.wakeup()
    wakeup_reason = await pcu.get_wakeup_reason()
    assert any(['shutdown_requested state' in init_output for init_output in init_outputs])
    assert any(['deep_sleep state' in deep_sleep_output for deep_sleep_output in deep_sleep_outputs])
    assert any(['active state' in wakeup_output for wakeup_output in wakeup_outputs])
    assert wakeup_reason == pcu.WakeupReason.WAKEUP_REASON_USER_REQUEST


@pytest.mark.hardware_in_the_loop
@pytest.mark.asyncio
async def test_hil_shutdown_init_and_abort():
    init_outputs = await pcu.cmd.shutdown.init()
    abort_outputs = await pcu.cmd.shutdown.abort()
    assert any(['shutdown_requested state' in init_output for init_output in init_outputs])
    assert any(['active state' in abort_output for abort_output in abort_outputs])


@pytest.mark.hardware_in_the_loop
@pytest.mark.asyncio
async def test_hil_shutdown_init_with_scheduled_wakeup():
    now = datetime.now()
    later = datetime.now() + timedelta(minutes=1)
    await pcu._set_date(pcu.DateKind.now, now)
    await pcu._set_date(pcu.DateKind.wakeup, later)
    init_outputs = await pcu.cmd_shutdown_init()
    deep_sleep_outputs = await pcu.check_messages(6)
    assert any(
        ['shutdown_requested state' in init_output for init_output in init_outputs])
    assert any(['deep_sleep state' in deep_sleep_output for deep_sleep_output in
                deep_sleep_outputs])

    wakeup_outputs = await pcu.check_messages(120)
    assert any(['active state' in wakeup_output for wakeup_output in wakeup_outputs])
    wakeup_reason = await pcu.get_wakeup_reason()
    assert wakeup_reason == pcu.WakeupReason.WAKEUP_REASON_SCHEDULED


@pytest.mark.hardware_in_the_loop
@pytest.mark.asyncio
async def test_hil_shutdown_with_wakeup_into_hmi():
    init_outputs = await pcu.cmd.shutdown.init()
    assert any(
        ['shutdown_requested state' in init_output for init_output in init_outputs])

    deep_sleep_outputs = await pcu.check_messages(6)
    assert any(['deep_sleep state' in deep_sleep_output for deep_sleep_output in
                deep_sleep_outputs])

    button_pressed_outputs = await pcu.debugcmd.button_pressed(0)
    assert any(['hmi state' in button_pressed_output for button_pressed_output in
                button_pressed_outputs])

    wakeup_outputs = await pcu.debugcmd.wakeup()
    assert any(['active state' in wakeup_output for wakeup_output in wakeup_outputs])

    wakeup_reason = await pcu.get_wakeup_reason()
    assert wakeup_reason == pcu.WakeupReason.WAKEUP_REASON_USER_REQUEST
