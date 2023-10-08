import logging
from datetime import datetime
from enum import Enum
from typing import List, Optional

from serial import Serial

LOG = logging.getLogger(__name__)


class cmd:
    class shutdown:
        @staticmethod
        def init():
            return cmd_shutdown_init()

        @staticmethod
        def abort():
            return cmd_shutdown_abort()

    @staticmethod
    def dock():
        return cmd_dock()

    @staticmethod
    def undock():
        return cmd_undock()

    @staticmethod
    def wakeup():
        return cmd_wakeup()

    class power:
        class hdd:
            @staticmethod
            def on():
                return power(VoltageRail.hdd, DesiredState.on)

            @staticmethod
            def off():
                return power(VoltageRail.hdd, DesiredState.off)

        class fiveV:
            @staticmethod
            def on():
                return power(VoltageRail.fiveV, DesiredState.on)

            @staticmethod
            def off():
                return power(VoltageRail.fiveV, DesiredState.off)

        class bcu:
            @staticmethod
            def on():
                return power(VoltageRail.bcu, DesiredState.on)

            @staticmethod
            def off():
                return power(VoltageRail.bcu, DesiredState.off)


class debugcmd:
    @staticmethod
    def wakeup():
        return cmd_wakeup()

    @staticmethod
    def button_pressed(button_id: int):
        if button_id < 2:
            return call_pcu(f'debugcmd button_{button_id}_pressed')


class get:
    class date:
        @staticmethod
        def now():
            return _get_date(date_kind=DateKind.now)

        @staticmethod
        def wakeup():
            return _get_date(date_kind=DateKind.wakeup)

        @staticmethod
        def backup():
            return _get_date(date_kind=DateKind.backup)

    @staticmethod
    def dockingstate():
        return _get_dockingstate()

    @staticmethod
    def currentlog():
        return _get_currentlog()


    class analog:
        @staticmethod
        def stator_supply_sense():
            raise NotImplementedError

        @staticmethod
        def imotor_prot():
            raise NotImplementedError

        @staticmethod
        def vin12_meas():
            raise NotImplementedError

    class digital:
        @staticmethod
        def endswitch():
            raise NotImplementedError

        @staticmethod
        def docked():
            raise NotImplementedError


class set:
    class date:
        @staticmethod
        def now(timestamp: datetime):
            return _set_date(date_kind=DateKind.now, date=timestamp)

        @staticmethod
        def wakeup(timestamp: datetime):
            return _set_date(date_kind=DateKind.wakeup, date=timestamp)

        @staticmethod
        def backup(timestamp: datetime):
            return _set_date(date_kind=DateKind.backup, date=timestamp)




def call_pcu(command: str) -> List[str]:
    LOG.debug(f'calling pcu with {command}')
    command_bytes = (command + '\r\n').encode()
    with Serial('/dev/ttyACM1', baudrate=38400, timeout=0.5) as ser:  # timeout is critical
        ser.write(command_bytes)
        output = ser.read_until('ch>')
    output = output.decode().split('\n')
    LOG.debug(f'received {output}')
    return [o.strip() for o in output]


class DockingState(Enum):
    pcu_dockingState_unknown: str = "pcu_dockingState_unknown"
    pcu_dockingState9_inbetween: str = "pcu_dockingState9_inbetween"
    pcu_dockingState0_docked: str = "pcu_dockingState0_docked"
    pcu_dockingState7_12vFloating: str = "pcu_dockingState7_12vFloating"
    pcu_dockingState6_5vFloating: str = "pcu_dockingState6_5vFloating"
    pcu_dockingState5_allDocked5vOn: str = "pcu_dockingState5_allDocked5vOn"
    pcu_dockingState4_allDocked12vOn: str = "pcu_dockingState4_allDocked12vOn"
    pcu_dockingState3_allDockedPwrOn: str = "pcu_dockingState3_allDockedPwrOn"
    pcu_dockingState2_allDockedPwrOff: str = "pcu_dockingState2_allDockedPwrOff"
    pcu_dockingState1_undocked: str = "pcu_dockingState1_undocked"


class WakeupReason(Enum):
    WAKEUP_REASON_POWER_ON: str = "poweron"
    WAKEUP_REASON_USER_REQUEST: str = "requested"
    WAKEUP_REASON_SCHEDULED: str = "scheduled"


class AnalogMeasurement(Enum):
    IMOTOR_PROT: str = "imotor_prot"
    STATOR_SUPPLY_SENSE: str = "stator_supply_sense"
    VIN12_MEAS: str = "vin12_meas"


class DigitalMeasurement(Enum):
    HMI_BUTTON_0: str = "HMI_BUTTON_0"
    HMI_BUTTON_1: str = "HMI_BUTTON_1"
    UNDOCKED_ENDSWITCH: str = "UNDOCKED_ENDSWITCH"
    DOCKED: str = "DOCKED"


def _get_dockingstate():
    cmd = 'get dockingstate'
    outp = call_pcu(cmd)
    outp = _filter_output_payload(outp, cmd)[0]
    return DockingState(outp)


def _get_currentlog():
    cmd = 'get currentlog'
    response = call_pcu(cmd)
    currents_raw = _filter_output_payload(response, cmd)
    currents = [int(c) for c in currents_raw if c]
    return currents


def get_wakeup_reason() -> WakeupReason:
    cmd = 'get wakeupreason'
    wr_raw = _filter_output_payload(call_pcu(cmd), cmd)[0]
    return WakeupReason(wr_raw)


def _filter_output_payload(pcu_outputs: List[str], command_sent: str) -> List[str]:
    """
    returns the usable string from the overall pcu output

    pcu returns the command sent, its output and a new prompt like this
    [b'get date now\r\n', b'00:00:00:542 - 01-01-2000\n', b'ch> ']
    only the second entry is relevant here

    :param pcu_outputs:
    :return:
    """
    filtered = []
    for pcu_output in pcu_outputs:
        if 'ch>' in pcu_output:
            filtered.append(pcu_output.split('ch>')[1])
        elif any([
            command_sent in pcu_output,
        ]):
            continue
        else:
            filtered.append(pcu_output)
    filtered = [filtered_item for filtered_item in filtered if filtered_item]
    return filtered


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
    output_raw = call_pcu(command_str)
    if not any([f"{command.value} successful" in output_line for output_line in output_raw]):
        raise RuntimeError
    retval = _filter_output_payload(output_raw, command_str)
    return output_raw


def cmd_shutdown_init():
    return _send_command(Commands.shutdown, 'init')


def cmd_shutdown_abort():
    return _send_command(Commands.shutdown, 'abort')


def cmd_wakeup():
    return call_pcu('cmd wakeup')


class DateKind(Enum):
    now: str = "now"
    backup: str = "backup"
    wakeup: str = "wakeup"


def _datetime_to_pcu_timestring(date: datetime) -> str:
    return f"{date.year} {date.month} {date.day} {date.hour} {date.minute}"


def _pcu_timestring_to_datetime(pcu_output: str) -> datetime:
    return datetime.strptime(pcu_output, "%H:%M:%S - %d-%m-%Y")


def _set_date(date_kind: DateKind, date: datetime):
    command = f"set date " + date_kind.value + " " + _datetime_to_pcu_timestring(date)
    return call_pcu(command)


def _get_date(date_kind: DateKind) -> datetime:
    command = "get date " + date_kind.value
    date_raw = call_pcu(command)
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
