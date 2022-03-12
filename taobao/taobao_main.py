# -*- coding: UTF-8 -*-
import time

from appium import webdriver

desired_capabilities = {
    'platformName': 'Android',  # 系统
    'deviceName': '13d4cfdf',  # 移动设备号 adb devices 命令取
    'platformVersion': '10',  # 系统版本 adb -s 13d4cfdf shell getprop ro.build.version.release
    'appPackage': 'com.taobao.taobao',
    'appActivity': 'com.taobao.tao.welcome.Welcome',
    'noReset': False
}


class AppiumExec(object):
    def __init__(self):
        self.driver = webdriver.Remote(desired_capabilities=desired_capabilities)

    def execute(self, keyword):
        search = self.driver.find_element_by_accessibility_id("搜索栏")
        while True:
            if search:
                break
            time.sleep(3000)
        search.send_keys(keyword)


def main():
    keywords = ['美甲']
    spider = AppiumExec()
    for keyword in keywords:
        spider.execute(keyword)


if __name__ == '__main__':
    main()
