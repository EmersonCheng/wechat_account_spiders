#! /usr/bin/env python3
# *-* coding : utf-8 *-*

import new_wechat as module
from selenium import webdriver
import datetime

test_path = "D:\Program_Project\python\wechat\\temp"
driver = webdriver.Chrome(module.getChromedriverPath())
driver.set_window_size(1366, 768)

title = "Jacob Collier+Jonah Nilsson现场"
url = 'https://mp.weixin.qq.com/s?timestamp=1521645434&src=3&ver=1&signature=HuazA4q0uHgS-sys9MnoFaZi*sYezeO2IUwq-I-1MoWNtB4uSDoEtz6o729SSyyHkpjjJS3WSP068cH0XhtjaZRya-n4QtMsL0ab6IaKsqGLDZINXYmrkr7IMWOqgTb3y5Uf*-Uza5RyHSC12YBjGdv0KYZ7iH2Me2-XcMFTbw0='
# url = 'https://mp.weixin.qq.com/s?src=11&timestamp=1521651066&ver=768&signature=4x0SFkywaFz7nh6iW36lOvQrcJuWSyLrrDC5GiRO0X2yDwWu0sAu5G8jjw22rff*Ce4uIaNlXb*X6dFf5oHlOPn2JFEFPlJEDueySt22Arm186ILS*ZSduVVKyE0iNax&new=1'
time = datetime.datetime.strptime("2018-03-07", '%Y-%m-%d')
abstract = None
is_original = False
account = "KORG中国"
ao = module.Article(title, url, time, abstract, is_original, account)
try:
    module.downArticle(driver, ao, test_path)
except BaseException as e:
    print(e)
finally:
    driver.quit()

print('end')
