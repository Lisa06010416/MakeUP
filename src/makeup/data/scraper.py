import os
import time
import json
import wget
import re
import requests
from urllib.parse import urljoin
from selenium import webdriver
from collections.abc import Sequence
from bs4 import BeautifulSoup

from makeup.data.utils import is_image_path, create_dir
from makeup.utils.logmanager import get_logger
from abc import ABC, abstractmethod
from googlesearch import search
from dataclasses import dataclass, field
from collections import namedtuple

logger = get_logger(__name__)

class GoogleSearch():
    @staticmethod
    def search(web_url, **kwargs):
        return search(web_url, **kwargs)

switch_page_urls = namedtuple('switch_page_urls', 'oldest_page, last_page, newest_page, next_page')

@dataclass
class Article:
    url: str
    title: float = ""
    images: list = field(default_factory=lambda: [])
    text: str = ""
    other: dict = field(default_factory=lambda: {})


class Scraper(ABC):
    @abstractmethod
    def get_webdata(self, url, **kwargs):
        pass

    @staticmethod
    def download_from_url(url, savepath=None):
        create_dir(savepath)
        filename = wget.detect_filename(url)
        if not os.path.isfile(os.path.join(savepath,filename)):
            try:
                wget.download(url, out=savepath)
                logger.info("Download file {} success".format(url))
            except:
                logger.info("Download file {} fail".format(url))

    @staticmethod
    def download_from_urllist(url_list, savepath):
        for image_url in url_list:
            Scraper.download_from_url(image_url, savepath)



class RequestScraper(Scraper):
    def __init__(self, **kwargs):
        pass

    def get_webdata(self, url, **kwargs):
        resp = requests.get(url, **kwargs)
        return BeautifulSoup(resp.content, 'html.parser')




class SeleniumScraper(Scraper):
    def __init__(self, options=None, executable_path=None, **kwargs):
        chromedriver = self._get_chromedriver(options, executable_path, **kwargs)
        self.chrome = chromedriver

    def get_webdata(self, url, **kwargs):
        self.chrome.get(url)
        self.chrome.implicitly_wait(5)
        try:  # 您的連線不是私人連線
            go_button = self.chrome.find_element_by_id("details-button")
            go_button.click()
            go_button = self.chrome.find_element_by_id("proceed-link")
            go_button.click()
        except:
            pass
        time.sleep(5)  # !!
        return BeautifulSoup(self.chrome.page_source, 'html.parser')

    @staticmethod
    def _get_chromedriver(options=None, executable_path=None, **kwargs):
        if not options:
            # https://intoli.com/blog/making-chrome-headless-undetectable/
            options = webdriver.ChromeOptions()
            options.add_experimental_option('useAutomationExtension', False)
            options.add_experimental_option('excludeSwitches', ['enable-automation'])

            #!! 沒開時自動開（？ 如何部署（？
            if kwargs.get("use_proxy"):
                # run_proxy_server("inject_js/inject.py") # cross env
                options.add_argument('--proxy-server=http://' + "localhost:8080")

            # 更換user agent
            user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
            options.add_argument(f'user-agent={user_agent}')

            options.add_argument("--disable-notifications")
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--no-sandbox')

            options.add_argument("headless")

        chromedriver = webdriver.Chrome(executable_path=executable_path,
                                        chrome_options=options)
        assert chromedriver, "Cannot get chromedriver"

        chromedriver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
          """
        })

        return chromedriver


class PttScraper(RequestScraper):
    def __init__(self,
                 domain_name="https://",
                 board_url="https://",
                 **kwargs):
        super().__init__(**kwargs)
        self.domain_name = domain_name
        self.board_url = board_url

    @classmethod
    def get_scraper(cls, **kwargs):
        # 指定新的父類別 => 給子類別用的
        base = kwargs.pop("base", None)
        if base:
            cls.__bases__ = (base,)
        return cls(**kwargs)

    def get_article_detail(self, article):
        article_url = self.domain_name + article.url
        soup = self.get_webdata(article_url)
        article_and_command = soup.find("div", id="main-container")

        # article_meta info
        article_meta_soup = article_and_command.find_all(class_=re.compile("article-meta-.*"))
        article_meta_list = self._get_attrs_and_text(article_meta_soup)
        article_meta = {}
        for idx in range(0, len(article_meta_list), 2):
            article_meta[article_meta_list[idx]['text']] = article_meta_list[idx + 1]['text']
        article.other["article_meta"] = article_meta
        article.title = article_meta["標題"]

        # push
        push_soup = article_and_command.find_all("span", class_=re.compile("push.*"))
        push_list = self._get_attrs_and_text(push_soup)
        push_idx = 0
        push_info_list = []
        while push_idx < len(push_list):
            if "push-tag" in push_list[push_idx]['class']:
                push_info_list.append(
                    {
                        "push-tag": push_list[push_idx]['text'],
                        "push-userid": push_list[push_idx + 1]['text'],
                        "push-conten": push_list[push_idx + 2]['text'],
                        "push-ipdatetime": push_list[push_idx + 3]['text']
                    }
                )
                push_idx += 4
            else:
                push_idx += 1

        # get image path
        image_soup = article_and_command.find_all("a")
        image_soup_list = self._get_attrs_and_text(image_soup)
        for index, info in enumerate(image_soup_list):
            href = info['href']
            if is_image_path(href):
                article.images.append(href)

        # text
        text = re.sub("(<.*>)|(<span.*)|(\">[./: \t\d+]+)|(※.*)|(--\n)", "", str(article_and_command))
        article.text = "\n".join([line for line in text.split("\n") if line.strip()])

    def get_articlelist_and_switchurls_from_contenturl(self, url):
        soup = self.get_webdata(url)

        # gat articles in content url
        article_list = []
        resultset = soup.find_all("div", class_='title')
        for result in resultset:
            article_anchor = result.find('a')
            info = self._get_attrs_and_text(article_anchor)[0]
            article = Article(url=info['href'], title=info['text'])
            article_list.append(article)

        # get urls used for switch pages
        switch_urls = self._get_change_contens_url(soup)
        return article_list, switch_urls

    def _get_change_contens_url(self, soup):
        button_info = soup.find_all("a", class_="btn wide")
        button_info = self._get_attrs_and_text(button_info)
        newest_page = None
        oldest_page = None
        last_page = None
        next_page = None
        for button in button_info:
            if "最舊" in button['text']:
                oldest_page = button['href']
            elif "上頁" in button['text']:
                last_page = button['href']
            elif "最新" in button['text']:
                newest_page = button['href']
            elif "下頁" in button['text']:
                next_page = button['href']
        return switch_page_urls(oldest_page=oldest_page,
                                last_page=last_page,
                                newest_page=newest_page,
                                next_page=next_page)

    def get_articles(self, keyword=None, url=None, search_page_num=1):
        if not url:
            if keyword:
                url = urljoin(self.board_url, f"search?q={keyword}")
            else:
                url = self.board_url

        for _ in range(search_page_num):
            articles, switch_urls = self.get_articlelist_and_switchurls_from_contenturl(url)
            yield articles
            url = urljoin(self.domain_name, switch_urls.next_page)

    def download_images(self, savepath, search_page_num=1):
        articles = self.get_articles(search_page_num)
        for _ in range(search_page_num):
            for article in next(articles):
                self.get_article_detail(article)
                self.download_from_urllist(article.images, savepath)

    @staticmethod
    def _get_attrs_and_text(resultset):
        all_info = []
        if isinstance(resultset, Sequence):
            for r in resultset:
                attrs = {} if not r else r.attrs
                text = {} if not r else r.text
                attrs['text'] = text
                all_info.append(attrs)
        else:
            attrs = {} if not resultset else resultset.attrs
            text = None if not resultset else resultset.text
            attrs['text'] = text
            all_info.append(attrs)
        return all_info


class XiaohongshuScraper(SeleniumScraper):
    """
    一定要用SeleniumScraper
    小紅書目前是給一個小紅書貼文的網址，爬該網址裡面的圖
    小紅書的web沒有search的功能
    """
    image_w = 300
    image_h = 300

    def set_imagesize(self, w=300,h=300):
        self.image_w = w
        self.image_h = h

    def download_images(self, web_url):
        soup = self.get_webdata(web_url)
        # get image
        result = soup.find_all("i", style=lambda style: style and "background-image" in style)
        # resize image
        urls = []
        for image in result:
            url = image.get("style")
            url = url.split('background-image:url(')[1]
            url = url.split(');')[0]
            url = url if 'https' in url else "https:" + url
            urls.append(url)
        return urls


class DcardScraper(SeleniumScraper):
    """
    python 在繼承時
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_img_urlpath(self, soup):
        urls = []
        for i in str(soup).split('"'):
            if is_image_path(i):
                urls.append(i)
        return urls

    @classmethod
    def get_scraper(cls, **kwargs):
        # 指定新的父類別 => 給子類別用的
        base = kwargs.pop("base", None)
        if base:
            cls.__bases__ = (base,)
        return cls(**kwargs)

    def get_articles(self, keyword, limit=3, search_by="keyword"):
        search_path = "https://www.dcard.tw/service/api/v2/search/posts?limit={}&query={}".format(limit, keyword)
        soup = self.get_webdata(search_path)
        articles = []
        for info in json.loads(soup.text):
            article = Article(url=str(info["id"]))
            articles.append(article)
        return articles

    def get_article_detail(self, article):
        article_url = "https://www.dcard.tw/service/api/v2/posts/{}".format(article.url)
        soup = self.get_webdata(article_url)
        article.images = self.get_img_urlpath(soup)
        json_data = json.loads(self.get_webdata(article_url).text)
        article.title = json_data["title"]
        article.text = json_data["excerpt"]
        del json_data["id"], json_data["title"], json_data["excerpt"]
        article.other = json_data

    def download_images(self, keyword, savepath, limit=3):
        articles = self.get_articles(keyword, limit)

        for article in articles:
            self.get_article_detail(article)
            self.download_from_urllist(article.images, savepath)
