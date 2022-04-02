import hashlib
import json
import os
import random
import time

import uiautomator2 as u2


class Automator:
    def __init__(self):
        self.app = u2.connect()
        self.restart()

    def restart(self):
        self.app.app_start('com.shizhuang.duapp', stop=True)
        # 初始化到 购买 tag
        time.sleep(10)
        self.app.watcher.when('//*[@resource-id="com.shizhuang.duapp:id/iv_close"]').click()
        btn_mall = self.app.xpath('//*[@resource-id="com.shizhuang.duapp:id/rbtn_mall"]')
        if btn_mall.exists:
            btn_mall.click()


def process_item(keyword: str, automator: Automator, price_str: str):
    print('start process new item.....')

    time.sleep(random.randint(1, 3))

    all_text = automator.app.xpath('//android.widget.TextView').all()
    all_texts = [_.text.strip() for _ in all_text]
    sales = None
    prices = []
    image_size = 0
    image_size_start = 0

    max_length = -1
    product_name = None
    for text in all_texts:
        if len(text) > max_length:
            max_length = len(text)
            product_name = text  # 取最长的作为 product_name

        # 都是 1/6 1/5 之类的
        if not image_size and "/" in text:
            image_size_start = int(text.split('/')[0])
            image_size = int(text.split('/')[1])
        elif text.startswith('¥'):
            prices.append(text)
        elif '付款' in text and '想要' in text:
            sales = text

    if not prices:
        print(all_texts)
        return False

    product_id = None
    if product_name:
        product_id = hashlib.md5(product_name.encode('utf-8')).hexdigest()
    else:
        print(all_texts)
        exit(-1)

    base_dir = "/tmp/hdd/du/{}/{}/{}".format(keyword, price_str, product_id)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    result_path = os.path.join(base_dir, 'result.json')
    if os.path.exists(result_path):
        print('hit cache ... skip')
        return True  # local cache

    automator.app.screenshot(os.path.join(base_dir, 'main.png'))

    print('开始处理图片。。。image_size: {}'.format(image_size))
    for i in range(0, image_size - image_size_start - 1):
        automator.app.swipe(700, 300, 100, 300, 0.1)
        time.sleep(3)
        print("swipe...{}".format(i))

    automator.app.click(300, 300)
    time.sleep(0.5)

    image_names = []

    image_name = os.path.join(base_dir, '0.png')
    automator.app.screenshot(image_name)
    image_names.append(image_name)

    for i in range(1, image_size - 1):
        automator.app.swipe(100, 300, 700, 300, 0.1)
        print("swipe...{}".format(i))
        time.sleep(3)
        image_name = os.path.join(base_dir, str(i) + '.png')
        automator.app.screenshot(image_name)
        image_names.append(image_name)

    time.sleep(1)
    automator.app.click(500, 500)

    data = {
        'product_id': product_id,
        'price': prices[0],
        'original_price': prices[1] if len(prices) > 1 else prices[0],
        'product_name': product_name,
        'sales': sales,
        'image_names': image_names,
    }
    with open(result_path, 'w') as f:
        json.dump(data, f, ensure_ascii=False)
    print('🎉🎉🎉 。。。')
    print('\n')
    return True


def main():
    keywords = [
        "耳钉",
        "戒指",
        "耳夹",
        "手链",
        "吊坠"
    ]
    for keyword in keywords:
        prices = [100, 500, 1000, 10000, 300000]
        for index in range(len(prices) - 1):
            start_price = prices[index]
            end_price = prices[index + 1] + 1

            automator = Automator()
            process_keyword(keyword, automator, start_price, end_price)


def process_keyword(keyword: str, automator: Automator, start_price, end_price):
    time.sleep(5)
    # 主页面的搜索
    search = automator.app.xpath('//*[@resource-id="com.shizhuang.duapp:id/fvSearch"]')
    # 副页面搜索
    keyword_search = automator.app.xpath('//*[@resource-id="com.shizhuang.duapp:id/laySearchContent"]')
    if search.exists:
        search.set_text(keyword)
    elif keyword_search.exists:
        keyword_search.set_text(keyword)

    time.sleep(1)

    automator.app.xpath('//*[@resource-id="com.shizhuang.duapp:id/tvComplete"]').click()
    automator.app.implicitly_wait(10 * 3)

    # 按照销量排序
    automator.app.xpath('//*[@text="累计销量"]').click()

    automator.app.implicitly_wait(10 * 3)

    time.sleep(1)

    automator.app.xpath('//*[@text="筛选"]').click()

    automator.app.xpath(
        '//*[@resource-id="com.shizhuang.duapp:id/layMenuFilterView"]/android.widget.RelativeLayout[1]/androidx.recyclerview.widget.RecyclerView[1]/android.widget.LinearLayout[1]/androidx.recyclerview.widget.RecyclerView[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]') \
        .set_text(str(start_price))
    time.sleep(random.random() * 3)
    automator.app.xpath(
        '//*[@resource-id="com.shizhuang.duapp:id/layMenuFilterView"]/android.widget.RelativeLayout[1]/androidx.recyclerview.widget.RecyclerView[1]/android.widget.LinearLayout[1]/androidx.recyclerview.widget.RecyclerView[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[2]') \
        .set_text(str(end_price))

    # https://www.cnblogs.com/yoyoketang/p/10850591.html 隐藏键盘
    automator.app.press(4)

    tv_confirm = automator.app.xpath('//*[@resource-id="com.shizhuang.duapp:id/tvConfirm"]')
    tv_confirm.click()

    i = 0
    while i < 20:
        time.sleep(3)
        temp_lists = automator.app.xpath('//*[@resource-id="com.shizhuang.duapp:id/recyclerView"]/android.view.ViewGroup').all()
        for item in temp_lists:
            item.click()
            automator.app.implicitly_wait(20)
            flag = process_item(keyword, automator, "{}_{}".format(start_price, end_price))
            if flag:
                # 返回到上一个页面
                automator.app.swipe(0, 900, 300, 900, 0.1)
        i += 1
        # 向下滑动
        automator.app.swipe(300, 1000, 300, 300, 0.08)
        automator.app.implicitly_wait(10)


if __name__ == '__main__':
    main()
