# -*- coding: UTF-8 -*-
import logging
import os

from selenium.webdriver.common.keys import Keys

from selenium_hdd import SeleniumHdd

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    datefmt='%Y-%m-%d %I:%M:%S',
    handlers=[
        logging.FileHandler("runtime.log"),
        logging.StreamHandler()
    ]
)

selenium_hdd = SeleniumHdd()
keywords_path = './keywords'


def get_all_keywords():
    with open(keywords_path, 'r') as f:
        for line in f.readlines():
            yield line


def process_keyword(keyword: str):
    logging.info("Start processing keyword: %s" % keyword)
    selenium_hdd.get('https://detail.1688.com/offer/559289957765.html')

    # input_elm = selenium_hdd.input("//*[@placeholder ='请输入关键词']", keyword)
    # from selenium.webdriver.common.keys import Keys
    # input_elm.send_keys(Keys.ENTER)


def main():
    selenium_hdd.get('https://www.1688.com/')
    for keyword in get_all_keywords():
        process_keyword(keyword.strip())


if __name__ == '__main__':
    # some check
    if not os.path.exists(keywords_path):
        logging.info("keywords file not exists, exit")
        exit()
    main()
