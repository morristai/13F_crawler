import logging
from time import strftime
import pandas as pd

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
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

if __name__ == "__main__":
    from pre_defined import semester_list
    for i in semester_list:
        print(i)