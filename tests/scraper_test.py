import os
import wget
import shutil
import pytest
from bs4 import BeautifulSoup


from src.lisa.data.scraper import RequestScraper, SeleniumScraper, PttScraper


test_url = "https://www.google.com.tw/"

def get_soup_from_file(path):
    with open(path, 'r') as f:
        file = f.read()
    return BeautifulSoup(file, 'html.parser')

class TestRequestScraper:
    def setup(self):
        self.test_web_url = "https://www.google.com.tw/"
        self.test_img_url = ""

    def test_request_scraper(self):
        global test_url
        scraper = RequestScraper()
        soup = scraper.get_webdata(self.test_web_url)
        assert soup

    def test_download_from_url(self):
        savepath="testdata/image/"
        if os.path.isdir(savepath):
            shutil.rmtree(savepath)
        scraper = RequestScraper()
        scraper.download_from_url(self.test_img_url)
        assert os.path.isdir(savepath), "Didn't creat dir!"
        assert len(os.listdir()) != 1, "download from url error!"

    def test_download_images_from_list(self):
        savepath = "testdata/image/"
        if os.path.isdir(savepath):
            shutil.rmtree(savepath)
        scraper = RequestScraper()
        scraper.download_from_url([self.test_img_url]*3)
        assert os.path.isdir(savepath), "Didn't creat dir!"
        assert len(os.listdir()) != 3, "download from url error!"

    def teardown(self):
        if os.path.isdir("testdata"):
            shutil.rmtree("testdata")


class TestSeleniumScraper:
    def setup(self):
        self.test_web_url = "https://www.google.com.tw/"
        self.test_img_url = ""
        # w10
        chromedriver_url = "http://chromedriver.storage.googleapis.com/index.html?path=2.9/"
        wget.download(chromedriver_url, out="chromedriver.exe")
        # !!mac

    def test_get_webdata(self):
        scraper = SeleniumScraper(executable_path="chromedriver.exe")
        soup = scraper.get_webdata(self.test_web_url)
        assert soup

        scraper = SeleniumScraper.get_scraper(executable_path="chromedriver.exe")
        soup = scraper.get_webdata(self.test_web_url)
        assert soup


class TestPttScraper:
    def setup(self):
        self.test_web_url = "https://www.google.com.tw/"
        self.test_img_url = ""
        # w10
        chromedriver_url = "http://chromedriver.storage.googleapis.com/index.html?path=2.9/"
        wget.download(chromedriver_url, out="chromedriver.exe")
        # !!mac

        self.soup = get_soup_from_file("test/pttboard.txt")

    def test_scraper(self):
        # test get scraper
        scraper = PttScraper.get_scraper(domain_name="https://www.ptt.cc/",
                                         board_url="https://www.ptt.cc/bbs/MakeUp/index.html",
                                         search_page_num=1,
                                         executable_path="chromedriver.exe")
        assert scraper
        assert isinstance(scraper, SeleniumScraper)
        soup = scraper.get_webdata(self.test_web_url)
        assert soup

        # change  father class
        scraper = PttScraper.get_scraper(domain_name="https://www.ptt.cc/",
                                         board_url="https://www.ptt.cc/bbs/MakeUp/index.html",
                                         search_page_num=1,
                                         executable_path="chromedriver.exe",
                                         base=RequestScraper)
        assert scraper
        assert isinstance(scraper, RequestScraper)
        soup = scraper.get_webdata(self.test_web_url)
        assert soup


    def test_get_ppt_article_list(self):
        # load test data
        scraper = PttScraper.get_scraper(domain_name="https://www.ptt.cc/",
                                         board_url="https://www.ptt.cc/bbs/MakeUp/index.html",
                                         search_page_num=1,
                                         executable_path="chromedriver.exe")

        article_list = scraper.get_ppt_article_list(self.soup)
        assert article_list
        # 測試數量內容


    def test_get_attrs_and_text(self):
        pass

    def test_get_change_contens_button(self):
        pass

    def test_get_attrs_and_text(self):
        pass


class TestXiaohongshuScraper:
    def test_set_imagesize(self):
        pass

    def scraper(self):
        pass


class TestDcardScraper:
    def test_get_urlpath(self):
        pass

    def test_scraper(selfs):
        pass
