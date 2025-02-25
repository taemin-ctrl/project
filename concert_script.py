import pandas as pd
from selenium import webdriver as wb
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import requests

URL = "https://ticket.interpark.com/webzine/paper/TPNoticeList.asp?tid1=in_scroll&tid2=ticketopen&tid3=board_main&tid4=board_main"

# 웹페이지 열기기

driver = wb.Chrome()
driver.get(URL)

time.sleep(1)

link = driver.find_element(By.TAG_NAME, 'em')  # 링크 텍스트로 찾기

link.click()


time.sleep(100)
# 작업 후 종료
# driver.quit()