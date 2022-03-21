# -*- coding: UTF-8 -*-
import uiautomator2 as u2

app = u2.connect()

all_text = app.xpath('//android.widget.TextView').all()

all_text = [_.text.strip() for _ in all_text]

print(all_text)
