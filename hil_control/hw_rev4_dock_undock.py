from serial import Serial
from time import sleep
import pandas as pd


def call_pcu(command) -> list:
    print(f'calling pcu with {command}')
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
    return outputs


def post_process_outputs(outputs, plot_title="") -> list:
    lines = [line.decode() for line in outputs]
    lines = [line for line in lines if "i=" in line]
    lines = [line.split("i=")[1].replace('␊','') for line in lines]
    lines = [int(line) for line in lines]
    if plot_title:
        fig, ax = plt.subplots(1)
        ax.plot(lines)
        ax.set_title(plot_title)
        ax.set_ylabel('imotor_prot')
    return lines


def get_dockingstate():
    outp = call_pcu('get_dockingstate')
    for line in outp:
        if 'pcu_docking' in line.decode():
            return line.decode().strip().split('ch> ')[1]


def dockingstate_good(dockingstate: str, command: str) -> bool:
    if command == 'undock' and dockingstate == 'pcu_dockingState1_undocked':
        return True
    elif command == 'dock' and dockingstate == 'pcu_dockingState2_allDockedPwrOff':
        return True
    else:
        return False


def run_test(iterations: int) -> list:
    test_runs = []
    df = pd.DataFrame({'iteration': [], 'current': [], 'command': []})

    for i in range(iterations):
        output_raw = call_pcu('dock')
        dock_currents = post_process_outputs(output_raw)
        dock_df = pd.DataFrame(
            {'iteration': [i] * len(dock_currents), 'current': dock_currents, 'command': ['dock'] * len(dock_currents)})
        dockingstate_after_docking = get_dockingstate()
        docking_good = dockingstate_good(dockingstate_after_docking, 'dock'),
        sleep(0.5)

        output_raw = call_pcu('undock')
        undock_currents = post_process_outputs(output_raw)
        undock_df = pd.DataFrame({'iteration': [i] * len(undock_currents), 'current': undock_currents,
                                  'command': ['undock'] * len(undock_currents)})
        dockingstate_after_undocking = get_dockingstate()
        undocking_good = dockingstate_good(dockingstate_after_undocking, 'undock')
        sleep(0.5)

        df = pd.concat([df, dock_df, undock_df])
        test_runs.append({
            "iteration": i,
            "dock_currents": dock_currents,
            "dockingstate_after_docking": dockingstate_after_docking,
            "docking_pass": docking_good,
            "undock_currents": undock_currents,
            "dockingstate_after_undocking": dockingstate_after_undocking,
            "undocking_pass": undocking_good
        })
        if not all([docking_good, undocking_good]):
            print(f"docking or undocking failed after {i} iterations")
            break
    return test_runs
