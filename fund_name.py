import re
import string
from time import strftime, sleep
import pandas as pd
import requests
from bs4 import BeautifulSoup
from pre_defined import header

today = strftime("%Y-%m-%d-%H")


def url_generator():
    url_queue = []
    for i in string.ascii_uppercase:
        url = f"https://www.insidermonkey.com/hedge-fund/browse/{i}/"
        url_queue.append(url)
    return url_queue


def get_id(urls):
    queue = []
    exception_catch = []
    for url in urls:
        resp = requests.get(url=url, headers=header, verify=True, timeout=3)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')
        # with open(f"{today}_{urls}_fund_id.html", "w") as file:
        #     file.write(str(soup))
        for idx, fund in enumerate(soup.findAll("div", {"class": "fund"})):
            row = fund.a.contents[0].split(" - ")
            row.append(re.sub('[^0-9]', '', fund.a['href'][-5:-1]))
            # idx prevent in case miss-match!
            queue.append(row)
        sleep(1)

    for idx, i in enumerate(queue):
        if len(i) != 3:
            exception_catch.append(queue.pop(idx))
            print(f"exception found:{i}")

    df = pd.DataFrame(queue, columns=['Fund', 'Manager', 'Id']).set_index('Id')
    return df


if __name__ == "__main__":
    page = url_generator()
    res = get_id(page)
    res.to_csv(f"{today}_fund_id.csv", encoding='utf8')
