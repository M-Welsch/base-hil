from time import sleep

import pandas as pd

from hil_control.testcase import Testcase
import hil_control.hw_rev4_pcu_interface as pcu


class HwRev4Statemachine(Testcase):
    def __init__(self):
        super().__init__()
        self.df = pd.DataFrame({'iteration': [], 'current': [], 'command': []})
        self.results = []

    def prepare(self):
        pcu.power(pcu.VoltageRail.hdd, pcu.DesiredState.off)
        pcu.power(pcu.VoltageRail.bcu, pcu.DesiredState.off)
        pcu.power(pcu.VoltageRail.fiveV, pcu.DesiredState.off)

    def issue_and_verify_shutdown_request(self):
        outputs = pcu.cmd.shutdown.init()
        assert any(["shutdown_requested state" in output for output in outputs])

    def issue_and_verify_shutdown_abort(self):
        outputs = pcu.cmd.shutdown.abort()
        assert any(["active state" in output for output in outputs])

    def run(self, iterations: int) -> None:
        self.issue_and_verify_shutdown_request()
        sleep(0.2)
        self.issue_and_verify_shutdown_abort()
