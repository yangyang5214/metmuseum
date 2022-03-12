# -*- coding: UTF-8 -*-

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class SeleniumHdd:

    def __init__(self):
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument("--disable-notifications")  # 屏蔽通知
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36')
        self.driver = webdriver.Chrome(
            executable_path='/Users/beer/java/chromedriver',
            chrome_options=chrome_options)
        with open('stealth.min.js') as f:
            js = f.read()
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": js
        })
        self.wait = WebDriverWait(self.driver, 10)

    def get(self, url):
        self.driver.get(url)

    def input(self, xpath, content):
        self.wait_xpath(xpath)
        element = self.xpath(xpath)
        element.send_keys(content)
        return element

    def xpath(self, xpath):
        return self.driver.find_element(by=By.XPATH, value=xpath)

    def wait_xpath(self, xpath):
        self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
