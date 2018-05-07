#! /usr/bin/env python3
# *-* coding : utf-8 *-*

# TODO:
# 1.验证码图片查看器picview可使用PyQt或wxWidget编写
# 2.检测代码可靠性，异常处理，兼容服务器或跨平台
# abort 3.方法1改进，不使用bs4解析网页源码，手动更改源码
# done 4.SQLite存储信息，防止重复下载
# done 5.284行abstract
#       soup.find_all('div', class_='weui_msg_card_bd')[0].
#       find_all('div',class_='weui_media_box appmsg')[0].
#       find_all(class_='weui_media_desc')[0].contents[0]
#   fix by using driver.set_window_size(1366, 768)
# 6.重构，改用面向对象方式
# 7.以纯解析的方式重新实现
# 8.加入不离线图片
# 9.编写qt离线查看器

from selenium import webdriver
from selenium.webdriver import Remote as WebDriver
import urllib
import bs4
import sqlite3
import progressbar
import datetime
import time
import os
import sys
import getopt
import json
import subprocess
import logging

logging.basicConfig(level=logging.WARNING)
SETTINGS_PATH = os.path.join(os.path.dirname(__file__), 'setting.json')
DATABASE_NAME = 'database.db'

# run py with argv
# sys.argv.append('--start')
# sys.argv.append('--non-headless')
# sys.argv.append('--disable-gpu')
# sys.argv.append('--download-all-article')

# sys.argv.append('--download-path')
# sys.argv.append('--set-download-path={0}'.format("../"))
# sys.argv.append('--account-list')
# sys.argv.append('--set-account={0}'.format("midifan"))
# sys.argv.append('--chromedriver-path')
# sys.argv.append('--set-chromedriver-path={0}'.format())


class Article(object):
    '''
        this object is store the article infomation,
        include title, url, datetime, abstract, is_original, account
    '''

    def __init__(self,
                 _title=None,
                 _url=None,
                 _datetime=None,
                 _abstract=None,
                 _is_original=False,
                 _account=None):
        self.title = _title
        self.url = _url
        self.datetime = _datetime
        self.abstract = _abstract
        self.is_original = _is_original
        self.account = _account

    def __str__(self):
        datetime_str = self.datetime.strftime('%Y-%m-%d')
        return '{}:"{}":{}'.format(datetime_str, self.title, self.url)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        if not isinstance(value, str) and value is not None:
            raise ValueError('title must be a string!')
        self._title = value

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        if not isinstance(value, str) and value is not None:
            raise ValueError('url must be a string!')
        self._url = value

    @property
    def datetime(self):
        return self._datetime

    @datetime.setter
    def datetime(self, value):
        if not isinstance(value, datetime.datetime) and value is not None:
            raise TypeError('datetime must be a datetime object!')
        self._datetime = value

    @property
    def abstract(self):
        return self._abstract

    @abstract.setter
    def abstract(self, value):
        if not isinstance(value, str) and value is not None:
            raise ValueError('abstract must be a string!')
        self._abstract = value

    @property
    def is_original(self):
        return self._is_original

    @is_original.setter
    def is_original(self, value):
        if not isinstance(value, bool):
            raise ValueError('is_original must be a boolean value!')
        self._is_original = value

    @property
    def account(self):
        return self._account

    @account.setter
    def account(self, value):
        if not isinstance(value, str) and value is not None:
            raise ValueError('account must be a string!')
        self._account = value


def processOutput(*args, **kw):
    print("#Process#", end=' ')
    for x in args:
        print(x, end=' ')
    if len(kw) != 0:
        print(kw)
    else:
        print("")


def checkFilename(str):
    escape_character = ['\\', '/', ':', '*', '?', '"', '<', '>', '|', ' ']
    for a in escape_character:
        if a in str:
            str = str.replace(a, '_')
    return str


def getSettings():
    if not os.path.exists(SETTINGS_PATH):
        return dict()
    with open(SETTINGS_PATH, 'r') as f:
        settings = json.load(f)
    return settings


def saveSettings(settings):
    if not isinstance(settings, dict):
        raise TypeError('settings must be a dict')
    with open(SETTINGS_PATH, 'w') as f:
        json.dump(settings, f, indent='\t')


def getDownloadPath():
    settings = getSettings()
    path = settings.get('download_path')
    if path is None:
        raise ValueError(
            'download path is empty, you need --set-download-path')

    if not os.path.exists(path):
        os.makedirs(path)
    else:
        logging.info("folder exist!")
    return path


def setDownloadPath(path):
    if not isinstance(path, str):
        raise ValueError('download path must be string')

    if not os.path.exists(path):
        os.makedirs(path)
    else:
        logging.info("folder exist!")

    settings = getSettings()
    settings['download_path'] = path
    saveSettings(settings)


def getAccountList():
    settings = getSettings()
    account_list = settings.get('account_list')
    if account_list is None:
        raise ValueError('account list is empty, you need --set-account')

    return account_list


def setAccountList(account_list):
    if not isinstance(account_list, list):
        raise ValueError('account list must be list')

    settings = getSettings()
    settings['account_list'] = account_list
    saveSettings(settings)


def getChromedriverPath():
    settings = getSettings()
    path = settings.get('chromedriver_path')
    if path is None:
        raise ValueError(
            'chromedriver path is empty, you need --set-chromedriver-path')

    return path


def setChromedriverPath(path):
    if not isinstance(path, str):
        raise ValueError('chromedriver path must be string')

    settings = getSettings()
    settings['chromedriver_path'] = path
    saveSettings(settings)


def getArticleList(driver, account, is_get_one_day=False):
    logging.info("getArticleList")
    if not isinstance(driver, WebDriver):
        raise TypeError("driver must be a WebDriver object!")
    if not isinstance(account, str):
        raise TypeError("accout must be a string!")
    if not isinstance(is_get_one_day, bool):
        raise TypeError("is_get_one_day must be a boolean value!")

    # use wechat search in sogou and get accout link
    query_url = 'http://weixin.sogou.com/weixin?type=1&s_from=input&query='
    search_url = query_url + account
    logging.info("search_url: %s" % search_url)
    driver.get(search_url)
    link_element = driver.find_element_by_xpath("//a[@uigs='account_name_0']")
    account_url = link_element.get_attribute("href")
    logging.info("account_url: %s" % account_url)

    # collect Article List
    driver.get(account_url)
    base = "https://" + urllib.parse.urlparse(account_url).hostname

    while len(driver.find_elements_by_class_name("weui_label")):
        driver.get_screenshot_as_file("verifycode.png")
        subprocess_path = os.path.join(os.path.dirname(__file__), 'picview')
        process = subprocess.Popen([subprocess_path, "verifycode.png"])
        # pdb.set_trace()
        verifycode = ''
        while len(verifycode) != 4:
            try:
                verifycode = input(
                    "please enter the verification code(4 character):")
            except BaseException as e:
                processOutput("abort download")
                driver.quit()
                process.kill()
                raise EOFError("abort download")
        driver.find_element_by_id("input").send_keys(verifycode)
        driver.find_element_by_id("bt").click()
        process.kill()
        os.remove("verifycode.png")

    daypost_list = driver.find_elements_by_class_name("weui_msg_card_bd")
    article_list = []
    for index, day in enumerate(daypost_list):
        if is_get_one_day and index != 0:
            break
        one_day_element_list = daypost_list[index].find_elements_by_class_name(
            "weui_media_box")
        one_day_article_list = []
        for article in one_day_element_list:
            tmp = Article()
            tmp.title = article.find_element_by_class_name(
                "weui_media_title").text.strip()
            if len(article.find_elements_by_class_name("icon_original_tag")):
                tmp.is_original = True
                tmp.title = tmp.title.replace('原创 ', '')
            else:
                tmp.is_original = False
            tmp.url = urllib.parse.urljoin(
                base,
                article.find_element_by_class_name(
                    "weui_media_title").get_attribute("hrefs"))
            tmp.abstract = article.find_element_by_class_name(
                "weui_media_desc").text.strip()
            date_str = article.find_element_by_class_name(
                "weui_media_extra_info").text.strip().replace(
                    "年", '-').replace("月", '-').replace("日", '').replace(
                        '原创', '')
            tmp.datetime = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            tmp.account = account
            one_day_article_list.append(tmp)
        article_list.append(one_day_article_list)

    return article_list


def downArticle(driver, article_object, path):
    if not isinstance(driver, WebDriver):
        raise TypeError("driver must be a WebDriver object!")
    if not isinstance(article_object, Article):
        raise TypeError("article_object must be a Article object!")

    datetime_str = article_object.datetime.strftime('%Y-%m-%d')
    sql_path = os.path.join(getDownloadPath(), DATABASE_NAME)

    connect = sqlite3.connect(sql_path)
    cursor = connect.cursor()
    c = cursor.execute('SELECT Title FROM "{}" WHERE Datetime == ?;'.format(
        article_object.account), (datetime_str, ))
    for row in c:
        # print(row)
        if row[0] == article_object.title:
            processOutput("article exist")
            cursor.close()
            connect.close()
            return
    cursor.close()
    connect.close()

    dir_name = checkFilename(article_object.title + "_files")
    dirpath = os.path.join(path, article_object.account, datetime_str,
                           dir_name)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    driver.get(article_object.url)
    delay_time = 5
    processOutput("wait for page loading... (%ss)" % delay_time)
    time.sleep(delay_time)
    html = driver.page_source
    soup = bs4.BeautifulSoup(html, "lxml")

    try:
        is_rich_media = True
        driver.find_element_by_class_name("rich_media")
    except BaseException as e:
        is_rich_media = False
    if not is_rich_media:
        processOutput("it's no rich media")
        if soup.find(
                class_="video_info_mod video_overview_info_context") is None:
            raise EOFError("this page can't download:", article_object.url)
        soup.find('title').string = article_object.title
        link = soup.find_all(
            'link', attrs={
                'onerror': 'wx_loaderror(this)'
            })[0]
        link['href'] = 'https:' + link['href']
        lis = soup.find_all('li', class_='js_history_li recent_video tj_item')
        for li in lis:
            base = 'http://v.qq.com/x/search?opensearch=1&q='
            title = li.find_all('strong', class_='recent_video_title')[0].text
            li.wrap(soup.new_tag('a', href=base + title))
    else:
        # method 1 by webdriver.find_elements_by_xpath() and BeautifulSoup.find()
        # img_list = driver.find_elements_by_xpath('//img[@data-src]')
        # for img_element in img_list:
        #     img_url = img_element.get_attribute("data-src")
        #     img_name = img_url.split('/')[-2]
        #     # img_element.screenshot_as_png  # only useful in Firefox
        #     file_name = os.path.join(path, article_object.account,
        #                              datetime_str, dir_name, img_name)
        #     urllib.request.urlretrieve(img_url, file_name)
        #     tag = soup.find(attrs={"data-src": img_url})
        #     tag['src'] = "./"+dir_name+img_name

        # method 2 by BeautifulSoup.find_all()
        img_list = soup.find_all('img', attrs={"data-src": True})
        if len(img_list):
            widgets = [
                '#Process# download pictures: (',
                progressbar.SimpleProgress(), ') ',
                progressbar.Bar(),
                progressbar.Percentage(), ' ',
                progressbar.Timer()
            ]
            bar = progressbar.ProgressBar(
                max_value=len(img_list), widgets=widgets)
            for index, img_tag in enumerate(img_list):
                img_url = img_tag['data-src']
                img_name = img_url.split('/')[-2]
                file_name = os.path.join(path, article_object.account,
                                         datetime_str, dir_name, img_name)
                urllib.request.urlretrieve(img_url, file_name)
                img_tag['src'] = "./" + dir_name + '/' + img_name
                bar.update(index + 1)
            bar.finish()

        qr_code_tag = soup.find(id="js_pc_qr_code_img")
        if qr_code_tag is not None:
            if 'src' in qr_code_tag.attrs:
                qr_code_url = qr_code_tag['src']
                qr_code_name = "qr_code"
                file_name = os.path.join(path, article_object.account,
                                         datetime_str, dir_name, qr_code_name)
                urllib.request.urlretrieve(
                    'https://mp.weixin.qq.com' + qr_code_url, file_name)
                qr_code_tag['src'] = "./" + dir_name + '/' + qr_code_name

    htm_name = checkFilename(article_object.title)
    htm_file = os.path.join(path, article_object.account, datetime_str,
                            htm_name + '.htm')
    with open(htm_file, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify()))

    htm_path = "./" + article_object.account + '/' \
        + datetime_str + '/' + htm_name + '.htm'
    data = (article_object.title, htm_path, datetime_str,
            article_object.abstract, article_object.is_original)
    connect = sqlite3.connect(sql_path)
    connect.execute('''INSERT INTO "{}"
        (Title,URL,Datetime,Abstract,Is_original)
        VALUES (?, ?, ?, ?, ?);'''.format(article_object.account), data)
    connect.commit()
    connect.close()


def startDownload(is_headless_mode, is_disable_gpu, download_all_article):
    processOutput("start download")
    path = getDownloadPath()
    processOutput("download path:", path)
    account_list = getAccountList()
    processOutput("accout list:", account_list)

    # database
    sql_path = os.path.join(getDownloadPath(), DATABASE_NAME)
    connect = sqlite3.connect(sql_path)
    for account in account_list:
        result = connect.execute(
            "select * from sqlite_master where type='table' and name=?;",
            (account, ))
        if not len(list(result)):
            connect.execute('''CREATE TABLE "{}"
                (ID         INTEGER PRIMARY KEY NOT NULL,
                Title       TEXT    NOT NULL,
                URL         TEXT    NOT NULL,
                Datetime    TEXT    NOT NULL,
                Abstract    TEXT,
                Is_original BOOLEAN);'''.format(account))
    connect.commit()
    connect.close()

    # init webdriver
    chromedriver_path = getChromedriverPath()
    options = webdriver.ChromeOptions()
    if is_headless_mode:
        options.set_headless()
    if is_disable_gpu:
        options.add_argument('-disable-gpu')  # for server
    processOutput("open browser...")
    driver = webdriver.Chrome(chromedriver_path, chrome_options=options)
    driver.set_window_size(1366, 768)

    try:
        is_get_one_day = not download_all_article
        for index, account in enumerate(account_list):
            processOutput('================================================')
            processOutput("current accout:", account_list[index])
            article_lists = getArticleList(driver, account, is_get_one_day)
            for article_list in article_lists:
                for index, article_object in enumerate(article_list):
                    processOutput('------------------------------------------')
                    progress = "%s/%s:" % (index + 1, len(article_list))
                    processOutput(progress, article_object)
                    downArticle(driver, article_object, path)
    except BaseException as e:
        print(e)
    finally:
        processOutput('================================================')
        processOutput("close browser...")
        driver.quit()
        processOutput("done")


def main():
    '''
    options:
        --start                     start download
        --non-headless              start broswer without headless mode
        --disable-gpu               start broswer disable gpu
        --download-all-article      download all account articles
                                    instead of download latest day
    configure:
        --download-path             show download path
        --set-download-path         set download path
        --account-list              show account list
        --set-account               set account list
        --chromedriver-path         show chromedriver path
        --set-chromedriver-path     set chromedriver path
        -h, --help                  show help
    set account list:
        divide accounts name/id by ',' if you want download more than
        two account
            example:
                --set-account="midifan,python"
    '''

    longopts = [
        "set-download-path=", "set-account=", "set-chromedriver-path=",
        "download-path", "account-list", "chromedriver-path", "help",
        "non-headless", "disable-gpu", "download-all-article", "start"
    ]
    try:
        opts, argv = getopt.getopt(sys.argv[1:], "h", longopts)
    except getopt.GetoptError as e:
        print(e)
        quit()

    if len(opts) == 0 or ('-h', '') in opts or ('--help', '') in opts:
        print(main.__doc__)
    elif ('--download-path', '') in opts:
        download_path = getDownloadPath()
        print("download-path:", download_path)
    elif ('--account-list', '') in opts:
        account_list = getAccountList()
        print("account-list:", account_list)
    elif ('--chromedriver-path', '') in opts:
        chromedriver_path = getChromedriverPath()
        print("chromedriver-path:", chromedriver_path)
    else:
        for opt in opts:
            if '--set-download-path' in opt:
                setDownloadPath(opt[1])
                print("download-path:", opt[1])
            if '--set-account' in opt:
                setAccountList(opt[1].strip().split(','))
                print("account-list:", opt[1].strip().split(','))
            if '--set-chromedriver-path' in opt:
                setChromedriverPath(opt[1])
                print("chromedriver-path:", opt[1])
        if ('--start', '') in opts:
            is_headless_mode = not ('--non-headless', '') in opts
            is_disable_gpu = ('--disable-gpu', '') in opts
            download_all_article = ('--download-all-article', '') in opts
            startDownload(
                is_headless_mode=is_headless_mode,
                is_disable_gpu=is_disable_gpu,
                download_all_article=download_all_article)


if __name__ == '__main__':
    main()
