# MakeUP
自動當我們搜尋某個美妝產品時，幫我們把文章中的試色文章找出來

TODO :

- [ ] Download Model
- [ ] Simple Inference Function
- [ ] Incremental learning
- [ ] Inference Server

## 使用方式
安裝 package :
```
git clone https://github.com/Lisa06010416/MakeUP.git
cd MakeUP.git
pip install .
```

###  1. Simple Use ：

###  2. Run a Server

###  3. Train Your Model


## Project 功能與遇到的問題
#### 爬資料：
爬蟲環境設置：
* 自動下載對應版本的chromedriver(但寫完後發現可以用 webdriver-manager XDD)
```
from makeup.utils.envchecker import get_chrome_driver
get_chrome_driver()
```
* 在設定 headless的情況下爬蟲會被小紅書擋,因此參考 [這篇教學](https://intoli.com/blog/making-chrome-headless-undetectable/) 對我們的發出的request做修改，用下面的方法打開mitmdump server :

```
run mitmdump  :
from makeup.script import setup_mitmdump_server
setup_mitmdump_server()

close mitmdump  :
from makeup.script import close_mitmdump_server
close_mitmdump_server()
```

爬蟲功能 (tests/scraper_test.py) :
* 可以爬三個來源的資料 ： ptt(PttScraper)、dcard(DcardScraper)、小紅書(XiaohongshuScraper)
* 可以換要用來爬蟲的base : request、Selenium，但要爬小紅書的資料的話一定要用 Selenium + 開啟 mitmdump server
* 下載資料名字不要重複

#### 訓練：
* 使用EfficientNet作為圖片分類模型
* 因為想要直接用transformers的trainer，因此對EfficientNet做了部分修改(in tests/efficientnnt_test.py) :
```
from transformers import Trainer
from makeup.model.efficientnet import EfficientNetModify
trainer = Trainer(
            model= your EfficientNetModify model,
            ...)
```


### run mitmdump


## haha
* 介紹用法
* 爬蟲
    - get chrome driver
    - 小紅書被ban
    - 換request
* 訓練
* inference server
