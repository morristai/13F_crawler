import platform
from pathlib import Path, WindowsPath

import pandas as pd


class DumpFile:
    def __init__(self):
        pass

    @staticmethod
    def warehouse():
        if platform.system() == 'Windows':
            out_dir = Path(WindowsPath.home() / "Documents" / "Data")
            out_dir.mkdir(parents=True, exist_ok=True)
        else:
            # out_dir = Path(Path.home() / "Documents" / "Data")
            out_dir = Path("/mnt/c/Users/morris/Documents/Data")
            out_dir.mkdir(parents=True, exist_ok=True)

        return out_dir

    @staticmethod
    def thirteen_floor(fund):
        dir_ = DumpFile.warehouse() / "13f" / f"{fund}"
        dir_.mkdir(parents=True, exist_ok=True)
        return dir_


if __name__ == "__main__":

    # Create every folder by fund name
    df_fund = pd.read_csv('Data/2020-06-09-05_fund_id.csv', index_col="Id")
    for fd in df_fund.to_dict()['Fund'].items():
        target_fund = fd[1]
        # target_fund = target_fund.replace(' ', '_')
        dir_ = DumpFile().thirteen_floor() / f"{target_fund}"
        print(dir_)
        dir_.mkdir(parents=True, exist_ok=True)
