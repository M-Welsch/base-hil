import logging

from serial import Serial

LOG = logging.getLogger(__name__)


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


def cmd_dock():
    return call_pcu('cmd dock')


def cmd_undock():
    return call_pcu('cmd undock')


def cmd_power_hdd_on():
    return call_pcu('cmd power hdd on')


def cmd_power_hdd_off():
    return call_pcu('cmd power hdd off')


def cmd_power_5v_on():
    return call_pcu('cmd power 5v on')


def cmd_power_5v_off():
    return call_pcu('cmd power 5v off')


def cmd_power_bcu_on():
    return call_pcu('cmd power bcu on')


def cmd_power_bcu_off():
    return call_pcu('cmd power bcu off')


def cmd_shutdown_init():
    return call_pcu('cmd shutdown init', stringify=True)


def cmd_shutdown_abort():
    return call_pcu('cmd shutdown abort', stringify=True)


def cmd_wakeup():
    return call_pcu('cmd wakeup', stringify=True)

