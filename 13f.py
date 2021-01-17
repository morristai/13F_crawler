import logging
import pickle
from time import sleep, strftime
from typing import List
from collections import defaultdict
import pandas as pd
import requests
from bs4 import BeautifulSoup, Comment
from numpy import nan

from dump import DumpFile
from pre_defined import header


def log_init() -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s', datefmt='%Y%m%d %H:%M:%S')
    log_filename = strftime("%Y-%m-%d_%H_%M_%S.log")

    # ==== StreamHandler ====
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # ==== FileHandler ====
    fh = logging.FileHandler('log/' + log_filename)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)


def get_data(fund, semester) -> List:
    """
    :param fund: 基金id
    :param semester: 季度 e.g. 2020-03-31
    :return: 包含所有標的資料的原始 List[List]
    """
    queue = []
    offset = 0
    while True:
        url = url_generator(fund, offset, semester)
        try:
            resp = requests.get(url=url, headers=header, verify=True, timeout=10)
        except requests.exceptions.ReadTimeout as er:
            logging.error(f"{er}")
            # TODO: 先退出，semester不會記錄，要用 Retry
            break
        soup = BeautifulSoup(resp.text, 'html.parser')
        res = soup.find_all(class_=['even', 'odd'])
        if not res:
            break
        else:
            for idx, equity in enumerate(res):
                queue.append([])
                for element in equity(text=lambda text: isinstance(text, Comment)):
                    element.extract()
                for item in equity:
                    try:
                        c = item.get_text()
                        # TODO: more efficient way to avoid IndexError
                        if c == "":
                            queue[idx + offset].append(nan)
                        else:
                            queue[idx + offset].append(c)
                    # item is not Beautiful Tag
                    except AttributeError:
                        continue
        offset += 40
    return queue


def iter_fund(fund: dict, done: pd.DataFrame) -> None:
    """
    :param fund: 基金的id和名稱
    :param done: 已經完成的
    :return: None
    """

    for fund_id, target_fund in fund.items():
        except_catch = {}
        prefect = True
        # target_fund = target_fund.replace(' ', '_')
        # iterate semester
        for s in done.index:
            try:
                if done.loc[s, fund_id] == 1:
                    logging.info(f"===>> Already exist {fund_id} {target_fund}-{s.date()}")
                    continue
            except KeyError:
                pass

            fund_queue = get_data(fund_id, s.date())
            if not fund_queue:
                logging.warning(f"===>> Not Found! {fund_id} {target_fund}: {s.date()}")
                # if fund_id not in not_found:
                #     not_found[fund_id] = []
                # not_found[fund_id].append(s)
                continue
            else:
                for x, i in enumerate(fund_queue):
                    # check if list is qualify for making DataFrame
                    if len(i) != 7:
                        logging.warning(f"{target_fund} {s.date()}: {i}")
                        # prevent AssertionError
                        if s.date() not in except_catch:  # check if key exist.
                            prefect = False
                            except_catch[s.date()] = []
                        except_catch[s].append(fund_queue.pop(x))
            df = pd.DataFrame(fund_queue,
                              columns=['No.', 'Security', 'Ticker', 'Shares', 'Value (x$1000)', 'Activity(%)', 'Port(%)'])
            clean_data(df)
            dump_file(df, target_fund, s.date())
            logging.info(f"===>> Finish {fund_id} {target_fund}-{s.date()}")
            done.loc[s, fund_id] = 1
            sleep(1.5)  # 暫緩2秒 TODO: 並行

        # 儲存except catch
        if not prefect:
            pd.DataFrame.from_dict(except_catch).to_csv(f"Data/exception/{target_fund}_except_catch.csv", index=False)

    # also save as DataFrame format
    now = strftime("%Y-%m-%d_%H_%M")
    done.fillna(0, inplace=True)
    done.to_csv(f"Cache/done_queue.csv")


def dump_file(df, target_fund, semester) -> None:
    """
    :param df: 準備Dump的DataFrame
    :param target_fund: 目標基金名稱
    :param semester: 季度
    :return: None
    """
    # mlc.save(df, f'{target_fund}_{s}.feather')
    prefix = DumpFile().thirteen_floor(target_fund)
    # target_fund = target_fund.replace(' ', '_')
    df.to_csv(f'{prefix}/{target_fund}_{semester}.csv', index=False)


def clean_data(df) -> None:
    """
    Logic: if call->1, put->2, equity->0
    :param df: pd.DataFrame
    :return: None
    """
    df.drop(['No.'], axis=1, inplace=True)
    df.loc[:, 'Security'] = df['Security'].replace(to_replace=r'PUTPUT', value=' PUT', regex=True)
    df.loc[:, 'Security'] = df['Security'].replace(to_replace=r'CALLCALL', value=' CALL', regex=True)
    df.loc[:, 'Security'] = df['Security'].replace('CALL$', ' (CALL)', regex=True)
    df.loc[:, 'Security'] = df['Security'].replace('PUT$', ' (PUT)', regex=True)
    df.loc[:, 'Security'] = df['Security'].replace('BOND$', ' (BOND)', regex=True)
    df.loc[:, 'Activity(%)'] = df['Activity(%)'].replace(to_replace=r'NEW', value='0%')
    df.loc[:, 'Activity(%)'] = df['Activity(%)'].apply(lambda x: x[:-1] if pd.notnull(x) else x).astype(float)
    df.loc[:, 'Port(%)'] = df['Port(%)'].apply(lambda x: x[:-1] if pd.notnull(x) else x).astype(float)
    df.loc[:, 'Value (x$1000)'] = df['Value (x$1000)'].apply(lambda x: x[1:] if pd.notnull(x) else x).str.replace(',','').astype(int)
    df.loc[:, 'Shares'] = df['Shares'].str.replace(',', '').astype(int)
    df.loc[:, 'Note'] = nan
    df.loc[df['Security'].str.find("(CALL)", 1) != -1, 'Note'] = "CALL"
    df.loc[df['Security'].str.find("(PUT)", 1) != -1, 'Note'] = "PUT"
    df.loc[df['Security'].str.find("(BOND)", 1) != -1, 'Note'] = "BOND"
    # Clean Note if only contains 0
    # df=df[[i for i in df if len(set(df[i]))>1]]
    return df


def url_generator(fund: str, offset: int, semester: str) -> str:
    prefix = "https://www.insidermonkey.com/services/get_fund_holdings.php"
    fot = 5  # by value
    fso = 1  # ascending
    # offset: Starting row
    return f"{prefix}?hfid={fund}&module=holdings&fundType=0&ffp={semester}&fot={fot}&fso={fso}&offset={offset}"


if __name__ == "__main__":
    log_init()

    df_fund = pd.read_csv('Data/2020-06-09-05_fund_id.csv', index_col="Id")
    # TODO: 451~452  501
    a = ['3']
    df_fund = df_fund[df_fund.index.isin(a)]
    df_fund = df_fund.to_dict()['Fund']

    done = pd.read_csv('Cache/done_queue.csv', index_col="semester", parse_dates=True)
    done.columns = done.columns.astype(int)
    # # Start Scraping
    iter_fund(df_fund, done)

