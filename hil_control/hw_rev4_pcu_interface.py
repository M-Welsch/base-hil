import logging

from serial import Serial

LOG = logging.getLogger(__name__)


def call_pcu(command) -> list:
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


def cmd_dock():
    call_pcu('cmd dock')


def cmd_undock():
    call_pcu('cmd undock')


def cmd_power_hdd_on():
    call_pcu('cmd power hdd on')


def cmd_power_hdd_off():
    call_pcu('cmd power hdd off')