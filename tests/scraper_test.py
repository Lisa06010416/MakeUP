import pytest
from src.lisa.data.scraper import RequestScraper

test_url = "https://www.google.com.tw/"


def selenium_setup():
    pass


class TestScraper:
    def setup(self):
        print("~~~~~~")

    def test_request_scraper(self):
        scraper = RequestScraper()
        soup = scraper.get_webdata(test_url)
        assert soup


class TestSeleniumScraper:
    def test_get_scraper(self):
        pass

    def test_get_webdata(self):
        pass


class TestPttScraper:
    def test_scraper(self):
        pass

    def test_get_ppt_article_list(self):
        pass

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
