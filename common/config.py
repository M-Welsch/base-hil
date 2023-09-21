import yaml


def load_configfile() -> dict:
    with open("config.yaml", "rt") as cfg_file:
        return yaml.safe_load(cfg_file.read())
