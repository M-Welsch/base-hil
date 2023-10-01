import logging.config
from datetime import datetime
from pathlib import Path

import pandas as pd

from common.config import load_configfile


timestamp = datetime.now().strftime("%Y-%m-%d %H-%M")


def logger_init():
    cfg = load_configfile()
    cfg["logging"]["handlers"]["file"]["filename"] = Path.cwd()/f"log/{timestamp}.log"
    logging.config.dictConfig(cfg["logging"])


def save_dataframe(df: pd.DataFrame):
    df.to_pickle(f"result/{timestamp}.pcl")
