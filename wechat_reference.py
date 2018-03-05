#! /usr/bin/env python3
from selenium import webdriver
# from datetime import datetime
import bs4
import requests
import os
import time
import sys


# 获取公众号链接
def getAccountURL(searchURL):
    res = requests.get(searchURL)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, "lxml")
    # 选择第一个链接
    account = soup.select('a[uigs="account_name_0"]')
    return account[0]['href']


# 获取首篇文章的链接，如果有验证码返回None
def getArticleURL(accountURL):
    jspath = "D:\Program_Project\python\wechat\phantomjs\\bin\phantomjs"
    browser = webdriver.PhantomJS(jspath)
    # 进入公众号
    browser.get(accountURL)
    # 获取网页信息
    html = browser.page_source
    accountSoup = bs4.BeautifulSoup(html, "lxml")
    time.sleep(1)

    # test
    verify = accountSoup.find_all('label')
    if verify[0].text == "验证码":
        print("warning: it's need verify code")
        raise Exception()
    # ~test

    contents = accountSoup.find_all(hrefs=True)
    try:
        partitialLink = contents[1]['hrefs']
        firstLink = base + partitialLink
    except IndexError:
        firstLink = None
        print('CAPTCHA!')
    return firstLink


# 创建文件夹存储html网页，以时间命名
def folderCreation():
    # path = os.path.join(os.getcwd(), datetime.now().strftime('%m-%d %H:%M'))
    # try:
    #     os.makedirs(path)
    # except OSError as e:
    #     if e.errno != errno.EEXIST:
    #         raise
    #     print("folder not exist!")
    path = os.path.join(os.getcwd(), "wechat", "test")
    if os.path.exists(path):
        print("folder exist!")
    else:
        os.makedirs(path)

    return path


# 将html页面写入本地
def writeToFile(path, account, title):
    pathToWrite = os.path.join(path, '{}_{}.html'.format(account, title))
    myfile = open(pathToWrite, 'wb')
    myfile.write(res.content)
    myfile.close()


base = 'https://mp.weixin.qq.com'
accountList = ['midifan']
query = 'http://weixin.sogou.com/weixin?type=1&s_from=input&query='
# query2 = 'http://weixin.sogou.com/weixin?type=1&query=%s'

path = folderCreation()

for index, account in enumerate(accountList):
    searchURL = query + account
    accountURL = getAccountURL(searchURL)
    time.sleep(5)
    articleURL = getArticleURL(accountURL)
    if articleURL is not None:
        lens = len(accountList)
        print("#{}({}/{}):{}".format(account, index+1, lens, accountURL))
        # 读取第一篇文章内容
        res = requests.get(articleURL)
        res.raise_for_status()
        detailPage = bs4.BeautifulSoup(res.text, "lxml")
        title = detailPage.title.text
        print("标题: {}\n链接: {}\n".format(title, articleURL))
        writeToFile(path, account, title)
    else:
        print('{} files successfully written to {}'.format(index, path))
        sys.exit()

print('{} files successfully written to {}'.format(len(accountList), path))
