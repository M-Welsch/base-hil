import logging
from time import sleep
import pandas as pd

from common.logger import logger_init
import hil_control.hw_rev4_pcu_interface as pcu
from hil_control.file_ops import FileOps

LOG = logging.getLogger(__name__)


def dockingstate_good(dockingstate: str, command: str) -> bool:
    if command == 'cmd undock' and dockingstate == 'pcu_dockingState1_undocked':
        return True
    elif command == 'cmd dock' and dockingstate == 'pcu_dockingState2_allDockedPwrOff':
        return True
    else:
        return False


class HwRev4DockUndock:
    def __init__(self):
        logger_init()
        self.file_ops = FileOps()
        self.df = pd.DataFrame({'iteration': [], 'current': [], 'command': []})
        self.results = []

    def prepare(self):
        self.file_ops.prepare()
        pcu.cmd_power_hdd_off()
        pcu.cmd_undock()

    def run(self, iterations: int) -> None:
        for i in range(iterations):
            pcu.cmd_dock()
            sleep(2)
            dock_currents = pcu.get_currentlog()
            dock_df = pd.DataFrame(
                {'iteration': [i] * len(dock_currents), 'current': dock_currents, 'command': ['dock'] * len(dock_currents)})
            dockingstate_after_docking = pcu.get_dockingstate()
            assert dockingstate_after_docking == "pcu_dockingState2_allDockedPwrOff"

            pcu.cmd_power_hdd_on()
            dockingstate_after_powering_hdd = pcu.get_dockingstate()
            assert dockingstate_after_powering_hdd == "pcu_dockingState3_allDockedPwrOn"

            datatransfer_rate_mb_per_s = self.file_ops.measure_datatransfer_rate()

            pcu.cmd_power_hdd_off()
            dockingstate_after_unpowering_hdd = pcu.get_dockingstate()
            assert dockingstate_after_unpowering_hdd == "pcu_dockingState2_allDockedPwrOff"

            pcu.cmd_undock()
            sleep(2)
            undock_currents = pcu.get_currentlog()
            undock_df = pd.DataFrame({'iteration': [i] * len(undock_currents), 'current': undock_currents,
                                      'command': ['undock'] * len(undock_currents)})
            dockingstate_after_undocking = pcu.get_dockingstate()
            assert dockingstate_after_undocking == "pcu_dockingState1_undocked"
            undocking_good = dockingstate_good(dockingstate_after_undocking, 'undock')
            sleep(0.5)

            self.df = pd.concat([self.df, dock_df, undock_df])
            self.results.append({
                "dock_currents": dock_currents,
                "dockingstate_after_docking": dockingstate_after_docking,
                "undock_currents": undock_currents,
                "dockingstate_after_undocking": dockingstate_after_undocking,
                "undocking_pass": undocking_good,
                "datatransfer_rate_mb_per_s": datatransfer_rate_mb_per_s
            })
        self.file_ops.cleanup_locally()