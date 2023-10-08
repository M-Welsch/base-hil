import logging
from datetime import datetime
from enum import Enum
from typing import List, Optional

from serial import Serial

LOG = logging.getLogger(__name__)


class cmd:
    @staticmethod
    def shutdown_init():
        return cmd_shutdown_init()


def call_pcu(command, stringify: bool = False) -> list:
    LOG.debug(f'calling pcu with {command}')
    outputs = []
    command_bytes = (command + '\r\n').encode()
    with Serial('/dev/ttyACM1', baudrate=38400, timeout=0.1) as ser:
        ser.write(command_bytes)
        all_read = False
        while not all_read:
            out = ser.read_until()
            outputs.append(out)
            if out == b'':
                all_read = True
    LOG.debug(f'returned {"".join([o.decode() for o in outputs])}')
    if stringify:
        try:
            outputs = ''.join([o.decode() for o in outputs]).split('\n')
            outputs = [o for o in outputs if o]
        except Exception:
            LOG.debug(f"couldn't preprocess call_pcu result: {[str(o) for o in outputs]}")
    return outputs


def get_dockingstate():
    outp = call_pcu('get dockingstate')
    for line in outp:
        if 'pcu_docking' in line.decode():
            return line.decode().strip()


def get_currentlog():
    outp = call_pcu('get currentlog')
    if not outp:
        outp = call_pcu('get currentlog')
    maxl = 0
    maxlidx = 0
    for idx, l in enumerate(outp):
        if len(l) > maxl:
            maxl = len(l)
            maxlidx = idx
    values_raw = outp[maxlidx].decode().strip().split(',')
    values = []
    for value_raw in values_raw:
        if not value_raw:
            continue
        try:
            values.append(int(value_raw))
        except Exception:
            values.append(0)
    return values


def get_wakeup_reason():
    cmd = 'get wakeupreason'
    return _filter_output_payload(call_pcu2(cmd), cmd)[0]


def _filter_output_payload(pcu_outputs: List[str], command_sent: str) -> List[str]:
    """
    returns the usable string from the overall pcu output

    pcu returns the command sent, its output, a prompt and an empty line like this
    [b'get date now\r\n', b'00:00:00:542 - 01-01-2000\n', b'ch> ', b'']
    only the second entry is relevant here

    :param pcu_outputs:
    :return:
    """
    for idx, pcu_output in enumerate(pcu_outputs):
        if 'ch>' in pcu_output:
            pcu_outputs.remove(pcu_output)
            pcu_outputs.insert(idx, pcu_output.split('ch>')[1])
        if any([
            command_sent in pcu_output
        ]):
            pcu_outputs.remove(pcu_output)
        pcu_outputs = [pcu_output for pcu_output in pcu_outputs if pcu_output]
    return pcu_outputs


def call_pcu2(command: str) -> List[str]:
    LOG.debug(f'calling pcu with {command}')
    command_bytes = (command + '\r\n').encode()
    with Serial('/dev/ttyACM1', baudrate=38400, timeout=0.5) as ser:  # timeout is critical
        ser.write(command_bytes)
        output = ser.read_until('ch>')
    output = output.decode().split('\n')
    LOG.debug(f'received {output}')
    return [o.strip() for o in output]


def check_messages(timeout_secs: float) -> Optional[List[str]]:
    with Serial('/dev/ttyACM1', baudrate=38400, timeout=timeout_secs) as ser:  # timeout is critical
        output = ser.read_until()
    output = output.decode().split('\n')
    LOG.debug(f'received {output}')
    return [o.strip() for o in output]


def cmd_dock():
    return call_pcu('cmd dock')


def cmd_undock():
    return call_pcu('cmd undock')


class Commands(Enum):
    shutdown: str = "shutdown"
    dock: str = "dock"
    undock: str = "undock"
    power: str = "power"
    wakeup: str = "wakeup"


def _send_command(command: Commands, *args):
    command_str = "cmd " + command.value + ' ' + ' '.join(args)
    output_raw = call_pcu2(command_str)
    if not any([f"{command.value} successful" in output_line for output_line in output_raw]):
        raise RuntimeError
    retval = _filter_output_payload(output_raw, command_str)
    return output_raw


def cmd_shutdown_init():
    return _send_command(Commands.shutdown, 'init')


def cmd_shutdown_abort():
    return _send_command(Commands.shutdown, 'abort')


def cmd_wakeup():
    return call_pcu('cmd wakeup', stringify=True)


class DateKind(Enum):
    now: str = "now"
    backup: str = "backup"
    wakeup: str = "wakeup"


def _datetime_to_pcu_timestring(date: datetime) -> str:
    return f"{date.year} {date.month} {date.day} {date.hour} {date.minute}"


def _pcu_timestring_to_datetime(pcu_output: str) -> datetime:
    return datetime.strptime(pcu_output, "%H:%M:%S - %d-%m-%Y")


def set_date(date_kind: DateKind, date: datetime):
    command = f"set date " + date_kind.value + " " + _datetime_to_pcu_timestring(date)
    return call_pcu2(command)


def get_date(date_kind: DateKind) -> datetime:
    command = "get date " + date_kind.value
    date_raw = call_pcu2(command)
    datestr = _filter_output_payload(pcu_outputs=date_raw, command_sent=command)[0]
    return _pcu_timestring_to_datetime(datestr)


class VoltageRail(Enum):
    hdd: str = "hdd"
    fiveV: str = "5v"
    bcu: str = "bcu"


class DesiredState(Enum):
    on: str = "on"
    off: str = "off"


def power(rail: VoltageRail, state: DesiredState):
    command = "cmd power " + rail.value + " " + state.value
    return call_pcu(command)