from datetime import datetime

import pytest

import hil_control.command_composer as composer


@pytest.mark.parametrize("command, command_str",
    [
    (composer.Cmd.power.fiveV.on, 'cmd power 5v on'),
    (composer.Cmd.power.fiveV.off, 'cmd power 5v off'),
    (composer.Cmd.dock, 'cmd dock'),
    (composer.Cmd.undock, 'cmd undock'),
    (composer.Get.date.backup, 'get date backup'),
    (composer.Set.date.now.to(datetime(1990, 9, 1, 12, 57)), 'set date now 1990 01 09 12 57'),
    (composer.Set.date.backup.to(datetime(2000, 1, 1, 0, 0)), 'set date backup 2000 01 01 00 00'),
    (composer.Set.date.wakeup.to(datetime(2001, 2, 2, 23, 31)), 'set date wakeup 2001 02 02 23 31'),
])
def test_command_composition(command, command_str):
    assert str(command) == command_str
