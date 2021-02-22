from googlesearch import search
from bs4 import BeautifulSoup
from selenium import webdriver

def googlesearch(keyword):
    return search(keyword, num_results=100)

def get_url(soup):
    for i in soup:
        print(i)
options = webdriver.ChromeOptions()
options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
options.add_argument("--disable-notifications")
options.add_argument("headless")
chrome = webdriver.Chrome('./chromedriver', chrome_options=options)

path = "https://www.xiaohongshu.com/discovery/item/602cd5e4000000000102507e"
chrome.get(path)
import time
time.sleep(5)
soup = BeautifulSoup(chrome.page_source, 'html.parser')
print(soup.prettify())