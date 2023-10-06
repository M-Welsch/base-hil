from datetime import datetime

class DateSubthing:
    def __init__(self, cmd):
        self.cmd = cmd.copy()

    def to(self, dt: datetime):
        if "set" in self.cmd:
            return " ".join(self.cmd) + dt.strftime(" %Y %d %m %H %M")
        else:
            return ''

    def __repr__(self):
        return " ".join(self.cmd)


class Date:
    def __init__(self, parentcmd):
        self.cmd = parentcmd.copy()
        self.cmd.append("date")
        self.now = DateSubthing([*self.cmd.copy(), "now"])
        self.backup = DateSubthing([*self.cmd.copy(), "backup"])
        self.wakeup = DateSubthing([*self.cmd.copy(), "wakeup"])


class Get:
    date = Date(["get"])


class Set:
    date = Date(["set"])


class Subthing:
    def __init__(self, cmd):
        self.cmd = cmd

    def __repr__(self):
        return " ".join(self.cmd)


class PowerSub:
    def __init__(self, cmd):
        self.on = Subthing([*cmd, "on"])
        self.off = Subthing([*cmd, "off"])


class Power:
    def __init__(self, cmd):
        self.hdd = PowerSub([*cmd, "hdd"])
        self.bcu = PowerSub([*cmd, "bcu"])
        self.fiveV = PowerSub([*cmd, "5v"])


class Shutdown:
    def __init__(self, cmd):
        self.init = Subthing([*cmd, "init"])
        self.abort = Subthing([*cmd, "abort"])


class Subcommand:
    def __init__(self, cmd):
        self.cmd = cmd.copy()

    def __repr__(self):
        return ' '.join(self.cmd)


class Cmd:
    shutdown = Shutdown(["cmd", "shutdown"])
    power = Power(["cmd", "power"])
    dock = Subcommand(["cmd", "dock"])
    undock = Subcommand(["cmd", "undock"])


if __name__ == "__main__":
    print("usage example: ")
    command_str = Set.date.now.to(datetime(1990, 9, 1, 12, 57))
    print(f"Set.date.now.to(datetime(1990, 9, 1, 12, 57) will output: {command_str}")
    print("more in test/test_unit_command_composer.py")
