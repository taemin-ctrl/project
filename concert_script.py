import os
from selenium import webdriver as wb
from selenium.webdriver.common.by import By
from datetime import datetime
import time
import json
import re
from selenium.webdriver.chrome.options import Options
import traceback

print("시작", flush=True)

# 날짜 포맷 변환 함수
def format_date(date_string):
    match = re.match(r'(\d{4})년 (\d{1,2})월 (\d{1,2})일', date_string)
    if match:
        year, month, day = match.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"
    return None

def format_apply(date_string):
    match = re.match(r'(\d{4}).(\d{1,2}).(\d{1,2})', date_string)
    if match:
        year, month, day = match.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"
    return None

# 현재 시간
current_time = datetime.now()
today = current_time.strftime("%Y-%m-%d")

# JSON 파일 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(current_dir, 'static', 'concert.json')

# JSON 파일 읽기
with open(json_file_path, "r", encoding="utf-8") as file:
    read_data = json.load(file)
print("json 파일 완료")

# 크롬 드라이버 실행 함수
def start_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return wb.Chrome(options=options)

driver = start_driver()
url = "https://ticket.interpark.com/webzine/paper/TPNoticeList.asp?tid1=in_scroll&tid2=ticketopen&tid3=board_main&tid4=board_main"
driver.get(url)
print("크롬 열기", flush=True)
time.sleep(1)

# iframe 전환
iframe = driver.find_element(By.ID, 'iFrmNotice')
driver.switch_to.frame(iframe)

# 첫 번째 페이지 링크 가져오기
first_pg = driver.find_elements(By.CSS_SELECTOR, "tbody a")
div = driver.find_elements(By.CLASS_NAME, "type")

div_list = [i.text for i in div[1:]]  # 첫 번째 요소 제외

print("click", flush=True)
time.sleep(1)

# 첫 페이지 클릭 및 iframe 해제
if div_list[0] != "HOT":
    first_pg[0].click()
else:
    first_pg[1].click()
    div_list.remove("HOT")

driver.switch_to.default_content()
time.sleep(2)
print("페이지 들어가기", flush=True)

num = 0
while num < 18:
    print(f"{num} 작업중", flush=True)
    try:
        concert_name = driver.find_elements(By.CSS_SELECTOR, "h3")
        w_regist_date = driver.find_elements(By.CLASS_NAME, "date")
        w_ticket_date = driver.find_elements(By.CLASS_NAME, "open")

        concert = concert_name[0].text.replace("단독판매", "").replace("상대우위", "")
        ticket_date = w_ticket_date[0].text.split("\n")[1]
        regist = w_regist_date[0].text[6:]

        time.sleep(3)
        
        a_tag = driver.find_element(By.CLASS_NAME, 'btn')
        link = a_tag.get_attribute('href') or driver.current_url

        time.sleep(3)

        try:
            next_pg = driver.find_element(By.CSS_SELECTOR, "li.next em > a")
            next_pg.click()
        except Exception as e:
            print(f"다음 페이지 이동 오류: {e}")
            break

        if not any(item.get('이름') == concert for item in read_data):
            read_data.append({
                "이름": concert,
                "구분": div_list[num],
                "예매날짜": format_date(ticket_date),
                "등록일": format_apply(regist),
                "링크": link,
                "checked": False,
                "active": True
            })
            with open(json_file_path, 'w', encoding='utf-8') as file:
                json.dump(read_data, file, ensure_ascii=False, indent=4)
            print(f"새 데이터 추가: {concert}")

        time.sleep(2)
        num += 1
    except Exception as e:
        print(f"오류 발생: {e}")
        traceback.print_exc()
        driver.quit()
        driver = start_driver()
        driver.get(url)
        time.sleep(1)

print("웹 크롤링 완료")
driver.quit()
