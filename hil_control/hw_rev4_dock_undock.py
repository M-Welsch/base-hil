import logging
from time import sleep, time
import pandas as pd

from common.logger import logger_init
import hil_control.hw_rev4_pcu_interface as pcu
from hil_control.file_ops import FileOps
from hil_control.testcase import Testcase

LOG = logging.getLogger(__name__)


def avg(l: list) -> float:
    return sum(l)/len(l)


class HwRev4DockUndock(Testcase):
    def __init__(self):
        super().__init__()
        self.file_ops = FileOps()
        self.df = pd.DataFrame({'iteration': [], 'current': [], 'command': []})
        self.results = []

    def prepare(self):
        self.file_ops.prepare()
        pcu.power(pcu.VoltageRail.hdd, pcu.DesiredState.off)
        pcu.cmd_undock()

    def run(self, iterations: int) -> None:
        pcu.power(pcu.VoltageRail.fiveV, pcu.DesiredState.on)
        for i in range(iterations):
            tick = time()
            pcu.cmd_dock()
            sleep(2)

            self._check_dockingstate(good_state="pcu_dockingState2_allDockedPwrOff")

            dock_currents = pcu.get_currentlog()
            dock_df = pd.DataFrame(
                {'iteration': [i] * len(dock_currents), 'current': dock_currents, 'command': ['dock'] * len(dock_currents)})
            sleep(1)

            pcu.power(pcu.VoltageRail.hdd, pcu.DesiredState.on)

            self._check_dockingstate(good_state="pcu_dockingState3_allDockedPwrOn")

            datatransfer_rate_mb_per_s = self.file_ops.measure_datatransfer_rate()

            pcu.power(pcu.VoltageRail.hdd, pcu.DesiredState.off)
            self._check_dockingstate(good_state="pcu_dockingState2_allDockedPwrOff")

            pcu.cmd_undock()
            sleep(2)
            undock_currents = pcu.get_currentlog()
            undock_df = pd.DataFrame({'iteration': [i] * len(undock_currents), 'current': undock_currents,
                                      'command': ['undock'] * len(undock_currents)})
            sleep(1)

            self._check_dockingstate(good_state="pcu_dockingState1_undocked")

            sleep(0.5)

            self.df = pd.concat([self.df, dock_df, undock_df])
            self.results.append({
                "dock_currents": dock_currents,
                "dockingstate_after_docking": "deprecated",
                "undock_currents": undock_currents,
                "dockingstate_after_undocking": "deprecated",
                "undocking_pass": False,  # deprecated
                "datatransfer_rate_mb_per_s": datatransfer_rate_mb_per_s
            })
            tock = time()
            LOG.info(
                f"finished run {i}. "
                f"Id_avg = {avg(dock_currents):.1f}, "
                f"Id_max = {max(dock_currents):.1f}, "
                f"Iud_avg {avg(undock_currents):.1f}, "
                f"Iud_max = {max(undock_currents):.1f}, "
                f"TR={datatransfer_rate_mb_per_s:.1f} MB/s, "
                f"t = {tock-tick:.1f}s"
            )
        self.file_ops.cleanup_locally()
        pcu.power(pcu.VoltageRail.fiveV, pcu.DesiredState.off)

    def _check_dockingstate(self, good_state: str, maximum_trials: int = 2, delay_between_trials: float = 1):
        trials = 0
        while not (dockingstate := pcu.get_dockingstate()) == good_state:
            if trials > maximum_trials:
                raise AssertionError(f"having {dockingstate} instead of {good_state}. Tried {trials} times")
            trials += 1
            sleep(delay_between_trials)
        LOG.debug(f"dockingstate correct after {trials+1} trials")

