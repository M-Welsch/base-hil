from common.logger import logger_init


class Testcase:
    def __init__(self):
        logger_init()

    def prepare(self):
        raise NotImplementedError

    def run(self, iterations: int) -> None:
        raise NotImplementedError
