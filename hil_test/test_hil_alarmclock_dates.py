from datetime import datetime, timedelta
from time import sleep

import pytest

import hil_control.hw_rev4_pcu_interface as pcu


@pytest.mark.parametrize("date_kind", [pcu.DateKind.now, pcu.DateKind.backup, pcu.DateKind.wakeup])
def test_set_get_date_now(date_kind: pcu.DateKind):
    nowish = datetime(2000, 1, 1, 0, 0)
    pcu.set_date(date_kind, nowish)
    sleep(0.2)
    later = pcu.get_date(date_kind)
    assert (later - nowish) < timedelta(seconds=2)
