from selenium import webdriver
from collections.abc import Sequence
from bs4 import BeautifulSoup


def get_attrs_and_text(resultset):
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


def get_ppt_article_list(soup):
    article_anchor_info = []
    resultset = soup.find_all("div", class_='title')
    for result in resultset:
        article_anchor = result.find('a')
        info = get_attrs_and_text(article_anchor)
        article_anchor_info.append(info[0])
    return article_anchor_info


def is_image(imagepath):
    if isinstance(imagepath, str):
        if imagepath.lower().endswith(('.bmp', '.dib', '.png', '.jpg', '.jpeg', '.pbm', '.pgm', '.ppm', '.tif', '.tiff')):
            return True
        else:
            return False

domain_name = "https://www.ptt.cc/"
options = webdriver.ChromeOptions()
options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
options.add_argument("--disable-notifications")
options.add_argument("headless")
chrome = webdriver.Chrome('./chromedriver', chrome_options=options)

print(type(chrome))
# chrome.get('https://www.ptt.cc/bbs/MakeUp/index.html')

# soup = BeautifulSoup(chrome.page_source, 'html.parser')

# btn wide

# def get_change_page_url(soup):
#     button = soup.find_all('a', class_="btn wide")
#     button_info = get_attrs_and_text(button)
#     up_page_path = ""
#     down_page_path = ""
#     for b in button_info:
#         if "上頁" in b['text'] and "href" in a:
#             up_page_path = domain_name + b['href']
#         elif "下頁" in b['text'] and "href" in b:
#             down_page_path = domain_name + b['href']
#     return up_page_path, down_page_path
