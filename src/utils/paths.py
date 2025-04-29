import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    raw_file_path: str = "data/raw/rawdata.csv"
    entry_point: str = "__main__"
