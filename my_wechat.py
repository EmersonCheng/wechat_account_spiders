#! /usr/bin/env python3
# *-* coding : utf-8 *-*

from selenium import webdriver
import bs4
import os
import logging


logging.basicConfig(level=logging.INFO)


class WechatBrowser(object):
    driver = None

    def __init__(self):
        # pass
        if WechatBrowser.driver is None:
            self.chromedriver_path = "d:\chrome\\Chrome\\chromedriver.exe"
            self.option = webdriver.ChromeOptions()
            # self.option.set_headless()
            # self.option.add_argument('-disable-gpu') # for server
            WechatBrowser.driver = webdriver.Chrome(self.chromedriver_path, chrome_options=self.option)

    def quit(self):
        # pass
        if WechatBrowser.driver is not None:
            WechatBrowser.driver.quit()

    def getAccoutArticleList(self, account, is_get_one_day):
        base = 'https://mp.weixin.qq.com'
        query_url = 'http://weixin.sogou.com/weixin?type=1&s_from=input&query='

        # use wechat search in sogou
        search_url = query_url + account
        logging.info("search_url: %s" % search_url)

        # get accout link and into accout page
        self.driver.get(search_url)
        html = self.driver.page_source
        soup = bs4.BeautifulSoup(html, "lxml")
        account_url = soup.select('a[uigs="account_name_0"]')[0]['href']
        logging.info("account_url: %s" % account_url)

        # test
        f = open(".\wechat\\midi_account.html", 'w', encoding='utf-8')
        f.write(html)
        f.close()
        # ~test

        self.driver.get(account_url)
        html = self.driver.page_source
        soup = bs4.BeautifulSoup(html, "lxml")

        # test
        f = open(".\wechat\\midi.html", 'w', encoding='utf-8')
        f.write(html)
        f.close()
        # ~test

        # Detecting whether a verification code
        verify = soup.find_all('label')
        if verify[0].text == "验证码":
            raise Exception('CAPTCHA!')

        # Get article list
        
        # element1 = self.driver.find_element_by_class_name("weui_media_extra_info")
        # element2 = self.driver.find_element_by_class_name("weui_media_title")
        # element3 = self.driver.find_element_by_class_name("weui_media_desc")
        # element4 = self.driver.find_element_by_class_name("weui_media_bd")
        import urllib, datetime
        urllib.parse.urlsplit(driver.current_url,'ss')
        datetime.datetime.strptime
        

        pass
        return ["test", "tmp"]

    def downArticle(self, article_url):
        pass


def setDownloadPath():
    # TODO :
    path = os.path.join(os.getcwd(), "wechat", "test")
    # END_TODO

    if not os.path.exists(path):
        os.makedirs(path)
    else:
        logging.info("folder exist!")
    return path


def setAccountList():
    # TODO :
    account_list = ['midifan']
    # END_TODO

    return account_list


def processOutput(_str, other=None):
    if other is not None:
        print("#Process#", _str, other)
    else:
        print("#Process#", _str)


if __name__ == '__main__':
    path = setDownloadPath()
    processOutput("download path:", path)
    account_list = setAccountList()
    processOutput("accout list:", account_list)
    browser = WechatBrowser()

    for index, account in enumerate(account_list):
        processOutput("current accout:", account_list[index])
        article_list = browser.getAccoutArticleList(account, True)
        processOutput("article list:", article_list)
        for article_url in article_list:
            browser.downArticle(article_url)

    browser.quit()
    processOutput("quit")
