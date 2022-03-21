import hashlib
import json
import os
import random
import time

import uiautomator2 as u2


class Automator:
    def __init__(self):
        self.app = u2.connect()
        self.app.app_start('com.taobao.taobao', stop=True)


def process_item(keyword: str, automator: Automator):
    print('start process new item.....')

    time.sleep(random.randint(5, 8))

    all_text = automator.app.xpath('//android.widget.TextView').all()
    all_texts = [_.text.strip() for _ in all_text]
    sales = None
    prices = []
    price_flag = False
    image_size = 0

    max_length = -1
    product_name = None
    for text in all_texts:
        if len(text) > max_length:
            max_length = len(text)
            product_name = text  # 取最长的作为 product_name

        if "/" in text and image_size == 0:
            image_size = int(text.split('/')[-1])

        if text == '￥':
            price_flag = True
        elif price_flag:
            prices.append(text)
            price_flag = False
        elif text.startswith('月销'):
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

    base_dir = "/tmp/hdd/{}/{}".format(keyword, product_id)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    else:
        print('hit cache ... skip')
        return True  # local cache

    print('开始处理图片。。。image_size: {}'.format(image_size))

    image_names = []
    for i in range(1, image_size):
        automator.app.swipe(400, 300, 100, 300, 0.1)
        time.sleep(random.randint(1, 3))

    print("滑动到最右边图片。。。。结束")

    time.sleep(1)
    automator.app.click(300, 300)
    time.sleep(1)

    image_name = os.path.join(base_dir, '0.png')
    automator.app.screenshot(image_name)
    image_names.append(image_name)

    for i in range(1, image_size - 1):
        automator.app.swipe(100, 300, 500, 300, 0.1)
        automator.app.implicitly_wait(10)
        time.sleep(random.randint(3, 5))
        image_name = os.path.join(base_dir, str(i) + '.png')
        automator.app.screenshot(image_name)
        image_names.append(image_name)

    time.sleep(1)
    automator.app.click(500, 500)

    data = {
        'product_id': product_id,
        'price': prices[0],
        'second_price': prices[1] if len(prices) > 1 else prices[0],
        'product_name': product_name,
        'sales': sales,
        'image_names': image_names,
    }
    with open(os.path.join(base_dir, 'result.json'), 'w') as f:
        json.dump(data, f)
    print('🎉🎉🎉 。。。')
    print('\n')
    return True


def process_keyword(keyword: str, automator: Automator):
    automator.app.xpath('//*[@content-desc="搜索栏"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[2]/android.widget.LinearLayout[1]').click()
    automator.app.xpath('//*[@resource-id="com.taobao.taobao:id/searchEdit"]').set_text(keyword)

    time.sleep(random.randint(3, 5))

    automator.app.press('enter')
    automator.app.implicitly_wait(10 * 3)

    # 按照销量排序
    try:
        automator.app.xpath('//*[@text="销量"]').click()
    except:
        print("xpath 失效，手动点击？")

    automator.app.implicitly_wait(10 * 3)

    i = 0
    while i < 20:
        time.sleep(3)
        temp_lists = automator.app.xpath('//*[@resource-id="com.taobao.taobao:id/libsf_srp_header_list_recycler"]/android.widget.FrameLayout').all()
        for item in temp_lists:
            item.click()
            automator.app.implicitly_wait(20)
            flag = process_item(keyword, automator)
            if flag:
                # 返回到上一个页面
                automator.app.swipe(0, 900, 300, 900, 0.1)
        i += 1
        # 向下滑动
        automator.app.swipe(300, 1000, 300, 300, 0.08)
        automator.app.implicitly_wait(10)


def main():
    # keywords = ['美甲片', '穿戴甲', '甲片']
    keywords = ['爱心项链', '爱心耳钉', '爱心戒指']
    for keyword in keywords:
        automator = Automator()
        process_keyword(keyword, automator)


# 爱心项链
# 三个关键词
# ['美甲片', '穿戴甲', '甲片']
#
# 每个关键词分别按销量和综合分别排序
#
# 按销量：
# 大的排序，开始拉，拉到月销量500左右结束
#
# 按综合
# 拉5页

if __name__ == '__main__':
    main()
