from time import sleep

import pytest

import hil_control.hw_rev4_pcu_interface as pcu


@pytest.mark.hardware_in_the_loop
def test_dock():
    """ abbreviating dockingstate as ps """
    pcu.cmd.power.fiveV.off()
    pcu.cmd.power.hdd.off()
    ds_right_before_docking = pcu.get.dockingstate()
    assert ds_right_before_docking == pcu.DockingState.pcu_dockingState1_undocked, "check if undocked, run again"
    pcu.cmd.dock()
    sleep(2)
    ds_after_docking_has_happened = pcu.get.dockingstate()
    assert ds_after_docking_has_happened == pcu.DockingState.pcu_dockingState2_allDockedPwrOff

    pcu.cmd.power.hdd.on()
    ds_after_power_hdd = pcu.get.dockingstate()
    assert ds_after_power_hdd == pcu.DockingState.pcu_dockingState4_allDocked12vOn

    pcu.cmd.power.fiveV.on()
    ds_after_power_5v = pcu.get.dockingstate()
    assert ds_after_power_5v == pcu.DockingState.pcu_dockingState3_allDockedPwrOn


@pytest.mark.hardware_in_the_loop
def test_undock():
    """ abbreviating dockingstate as ps """
    pcu.cmd.power.fiveV.on()
    pcu.cmd.power.hdd.on()

    ds_right_before_undocking = pcu.get.dockingstate()
    assert ds_right_before_undocking == pcu.DockingState.pcu_dockingState3_allDockedPwrOn, "check if docked, run again"

    pcu.cmd.power.fiveV.off()
    sleep(0.5)
    ds_after_unpower_5v = pcu.get.dockingstate()
    assert ds_after_unpower_5v == pcu.DockingState.pcu_dockingState4_allDocked12vOn

    pcu.cmd.power.hdd.off()
    ds_after_unpower_hdd = pcu.get.dockingstate()
    assert ds_after_unpower_hdd == pcu.DockingState.pcu_dockingState2_allDockedPwrOff

    pcu.cmd.undock()
    sleep(2)
    ds_after_undocking = pcu.get.dockingstate()
    assert ds_after_undocking == pcu.DockingState.pcu_dockingState1_undocked
