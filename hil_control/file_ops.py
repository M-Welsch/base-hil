import subprocess
import logging
from time import time, sleep
from pathlib import Path


from common.config import load_configfile

LOG = logging.getLogger(__name__)


class DatatransferRate(float):
    unit = "MB/s"


class FileOps:
    def __init__(self):
        self.config = load_configfile()["fileops"]
        self.mount_dir = Path(self.config["mntdir"])
        self.device_node = Path(self.config["device_node"])
        self.testfile_source = Path(self.config["testfile_temp_location"])
        self.testfile_target = self.mount_dir/self.config["testfile_name"]

    def __enter(self):
        self.prepare()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup_locally()

    def prepare(self):
        self.unmount()
        self.create_big_dummy_file(self.config["testfile_size_gb"])

    def measure_datatransfer_rate(self) -> DatatransferRate:
        self.wait_for_device_node()
        self.mount()
        if not self.mounted():
            LOG.error("not mounted!")
            return DatatransferRate(0.0)
        transfer_rate = self.copy_dummyfile_to_usbdrive()
        self.cleanup_usbdrive()
        self.unmount()
        return DatatransferRate(transfer_rate)  # self.config["testfile_size_gb"] * 1000 / duration

    def wait_for_device_node(self, timeout: float = 5):
        tick = time()
        while time() - tick < timeout:
            self.device_node.exists()
            sleep(0.1)

    def mount(self):
        max_trials = 3
        trials = 0
        while trials < max_trials:
            if subprocess.call(["mount", self.device_node.as_posix()]) == 0:
                return
            sleep(2)
        LOG.error(f"couldn't mount {self.device_node} withing {max_trials} trials")

    def unmount(self):
        subprocess.call(["umount", self.device_node.as_posix()])

    def mounted(self) -> bool:
        return self.mount_dir.is_mount()

    def create_big_dummy_file(self, size_gb: float) -> float:
        tick = time()
        blocksize = int(10*1024*1024)
        count = int(size_gb / blocksize * 1024 * 1024 * 1024)
        cmd = ["dd", "if=/dev/urandom", f'of={self.testfile_source.as_posix()}', f'count={count}', f'bs={blocksize}']
        LOG.debug(f"creating testfile with {' '.join(cmd)}")
        subprocess.call(cmd)
        tock = time()
        return tock - tick

    def copy_dummyfile_to_usbdrive(self):
        if not self.testfile_source.exists():
            LOG.warning("dummyfile doesn't exist. Creating real quick ...")
            self.create_big_dummy_file(self.config["testfile_size_gb"])
        if not self.mount_dir.is_mount():
            LOG.warning("USB Stick seems to be not mounted. Trying to mount now ...")
            self.mount()
        tick = time()
        cmd = ["cp", self.testfile_source.as_posix(), self.testfile_target.as_posix()]
        LOG.debug(f"copying testfile with {' '.join(cmd)}")
        subprocess.call(cmd)
        tock = time()
        return self.config["testfile_size_gb"] * 1024 / (tock - tick)

    def copy_dummyfile_to_usbdrive_rsync(self):  # buggy and ugly
        if not self.testfile_source.exists():
            LOG.warning("dummyfile doesn't exist. Creating real quick ...")
            self.create_big_dummy_file(self.config["testfile_size_gb"])
        if not self.mount_dir.is_mount():
            LOG.warning("USB Stick seems to be not mounted. Trying to mount now ...")
            self.mount()
        cmd = ["rsync", self.testfile_source.as_posix(), self.testfile_target.as_posix()]
        output = subprocess.check_output(cmd)
        try:
            lines = output.decode().split('\n')
            speedline = [l for l in lines if l.startswith('sent')][0]
            bytes_per_second = speedline.split('  ')[-1]  # like: '427.923.502,00 bytes/sec'
            bytes_per_second.split(',')
            tranfer_rate = int(bytes_per_second.split(',')[0].replace('.',''))
        except Exception as e:
            LOG.error(f"something went wrong here: {e}")
            tranfer_rate = 0
        return tranfer_rate / (1024 * 1024)


    def cleanup_usbdrive(self):
        subprocess.call(["rm", self.testfile_target])

    def cleanup_locally(self):
        subprocess.call(["rm", self.testfile_source])
