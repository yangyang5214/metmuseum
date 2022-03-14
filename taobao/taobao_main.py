import json
import random
import time

import uiautomator2 as u2


class Automator:
    def __init__(self):
        self.app = u2.connect()
        self.app.app_start('com.taobao.taobao', stop=True)


def process_item(automator: Automator):
    time.sleep(random.randint(5, 8))
    all_text = automator.app.xpath('//android.widget.TextView').all()
    sales = None
    prices = []
    product_name = None
    price_flag = False
    for item in all_text:
        text = item.text.strip()
        if text == '￥':
            price_flag = True
        elif price_flag:
            prices.append(text)
            price_flag = False
        elif item.text.startswith('月销'):
            sales = text
        elif sales and not product_name:
            product_name = text

        if product_name:
            break
    data = {
        'price': prices[0],
        'second_price': prices[1] if len(prices) > 1 else prices[0],
        'product_name': product_name,
        'sales': sales,
    }
    print(json.dumps(data, indent=4, ensure_ascii=False))


def process_keyword(keyword: str, automator: Automator):
    automator.app.xpath('//*[@content-desc="搜索栏"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[2]/android.widget.LinearLayout[1]').click()
    automator.app.xpath('//*[@resource-id="com.taobao.taobao:id/searchEdit"]').set_text(keyword)

    time.sleep(random.randint(3, 5))

    automator.app.press('enter')
    automator.app.implicitly_wait(10 * 3)
    while True:
        temp_lists = automator.app.xpath('//*[@resource-id="com.taobao.taobao:id/libsf_srp_header_list_recycler"]/android.widget.FrameLayout').all()
        for item in temp_lists:
            item.click() and automator.app.implicitly_wait(10)
            process_item(automator)
            automator.app.press('back')
        break


def main():
    automator = Automator()
    keywords = ['美甲']
    for keyword in keywords:
        process_keyword(keyword, automator)


if __name__ == '__main__':
    main()
