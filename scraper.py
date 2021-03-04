from src.lisa.data.data_crawler import PttScraper


scraper = PttScraper.get_scraper(domain_name="https://www.ptt.cc/",
                                      board_url="https://www.ptt.cc/bbs/MakeUp/index.html",
                                      scrapt_page_num=100,
                                      executable_path="C:/Users/Lisa/chromedriver_win32/chromedriver.exe")
articles = scraper.scraper(savepath="dataset/train/images")


from src.lisa.data.data_crawler import DcardScraper
scraper = DcardScraper.get_scraper(executable_path="C:/Users/Lisa/chromedriver_win32/chromedriver.exe")
articles = scraper.scraper(savepath="dataset/train/images", keyword="試色", limit=300)

