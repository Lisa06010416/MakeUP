from selenium import webdriver
from collections.abc import Sequence
from bs4 import BeautifulSoup


class BasicCrawler:
    def __init__(self, domain_name, home_path):
        self.domain_name = domain_name
        self.home_path = home_path
        self.chrome = self._get_webdriver()

    def _get_webdriver(self):
        options = webdriver.ChromeOptions()
        options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        options.add_argument("--disable-notifications")
        options.add_argument("headless")
        chrome = webdriver.Chrome('./chromedriver', chrome_options=options)
        return chrome

    def get_web(self, url):
        self.chrome.get(url)

    def get_soup(self, url=None):
        if url:
            self.get_web(url)
        return BeautifulSoup(self.chrome.page_source, 'html.parser')

    def get_attrs_and_text(aelf, resultset):
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

    def is_image(aelf, imagepath):
        if isinstance(imagepath, str):
            if imagepath.lower().endswith(
                    ('.bmp', '.dib', '.png', '.jpg', '.jpeg', '.pbm', '.pgm', '.ppm', '.tif', '.tiff')):
                return True
            else:
                return False


class PptCrawler(BasicCrawler):
    def _get_change_page_url(self, soup):
        button = soup.find_all('a', class_="btn wide")
        button_info = self.get_attrs_and_text(button)
        up_page_path = ""
        down_page_path = ""
        for b in button_info:
            if "上頁" in b['text'] and "href" in b:
                up_page_path = self.domain_name + b['href']
            elif "下頁" in b['text'] and "href" in b:
                down_page_path = self.domain_name + b['href']
        return up_page_path, down_page_path

    def get_page_list(self, num):
        page_list = [self.home_path]
        start_path = self.home_path
        for i in range(num-1):
            soup = self.get_soup(start_path)
            up_page_path, _ = self._get_change_page_url(soup)
            page_list.append(up_page_path)
            start_path = up_page_path
        return page_list

    def get_article_list(self, soup):
        article_anchor_info = []
        resultset = soup.find_all("div", class_='title')
        for result in resultset:
            article_anchor = result.find('a')
            info = self.get_attrs_and_text(article_anchor)
            article_anchor_info.append(info[0])
        return article_anchor_info
