from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class Text(object):
    def __init__(self,key):
        self.url = 'https://www.xiaohongshu.com/explore'
        chrome_opt = webdriver.ChromeOptions()
        chrome_opt.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        chrome_opt.add_argument("--headless")
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_opt.add_experimental_option("prefs", prefs)
        # 创建chrome无界面对象 options=chrome_opt
        self.driver = webdriver.Chrome('./chromedriver',options=chrome_opt)
        self.driver.get(self.url)
        self.key = key
        # self.driver.maximize_window()

    def get_input(self,xpath):
        btn = WebDriverWait(self.driver, 60).until(EC.visibility_of_element_located((By.XPATH, xpath)))
        return btn

    def __del__(self):
        pass
        # self.driver.quit()

    def get_data(self):
        res = self.driver.page_source
        soup = BeautifulSoup(res, 'html.parser')
        print(soup.prettify())

    def run(self):
        # 定位输入框
        put_btn = self.get_input('//input[@class="input"]')
        put_btn.send_keys(self.key)
        # 定位点击按钮
        # # 执行点击
        js = 'document.getElementsByClassName("search-icon")[0].click();'
        self.driver.execute_script(js)
        # click_btn.click()
        # # 解析内容,在此之前切换句柄
        self.driver.switch_to.window(self.driver.window_handles[1])
        # 解析获取数据
        self.get_data()



if __name__ == '__main__':
    key = input('请输入关键字:')
    a = Text(key)
    a.run()
