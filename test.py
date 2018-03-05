#! /usr/bin/env python3
# *-* coding : utf-8 *-*

import urllib
import requests
import bs4
import os

path = './wechat/test/'
# searchURL = "http://mp.weixin.qq.com/s?timestamp=1519885886&src=3&ver=1&signature=E*c2alvIo6ciuAQyr14vvcLFzhp8Htm1txfuvXi-xrBZwekEmqbLrIdDhZfhbICyVnH60nTJ5aD5UXDB6ej*4CupPPH4u3LzAeLUstpEXRefY*5jsgFlPcsQFDLEI8sn-lqDDS8NWadcJV5Jfx-Hw9p27Ybd6bHrO*6gpjVON-c="
searchURL = "http://mp.weixin.qq.com/s?timestamp=1519896117&src=3&ver=1&signature=TCrZiOS37b88ezNYvpddPlR*QKgcVOIpmdWawZqxKE7MoHjDGLBjHAtxxKW5YDAtmIv2bNBkumjFsBBG1r24iW*o3SxrN7QX56iw6Xxu8ygRqe9gJ9zKZQvnpAcMjGy9VDzJKgNX6tHook0TFxeeYd9qYZYppf4oKin6NClr1FQ="
# searchURL = "http://mp.weixin.qq.com/s?src=11&timestamp=1519899140&ver=728&signature=ydCTK356WvdA-YoRh8Rfg*hiJJQ5WzuKxb6yp7lBAyqKidQFfNaMazOPe4NOyZNa0jUUDfGhr6*EzwUGB8461oDDcE3Tn1IrOempoP0HAPAXWXtG3djA6ANUiF2MJD9v&new=1"
res = requests.get(searchURL)
res.raise_for_status()
soup = bs4.BeautifulSoup(res.text, "lxml")

title = str(soup.title.contents[0])
img_list = soup.find_all('img', attrs={"data-src": True})
for img_tag in img_list:
    img_url = img_tag['data-src']
    img_name = urllib.parse.urlparse(img_url).path.split('/')[-2]
    img_res = requests.get(img_url)
    img_res.raise_for_status()
    sub_dir_name = title+'_files/'
    img_tag['src'] = "./"+sub_dir_name+img_name
    if not os.path.exists(path+sub_dir_name):
        os.makedirs(path+sub_dir_name)
    with open(path+sub_dir_name+img_name, 'wb') as f:
        f.write(img_res.content)

read_more_tag = soup.find(id="js_toobar3")
if read_more_tag is not None:
    read_more_tag.decompose()
with open(path+title+'.htm', 'w', encoding='utf-8') as f:
    f.write(str(soup.prettify()))
