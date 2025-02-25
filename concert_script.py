from selenium import webdriver as wb
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import datetime
import time
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
from selenium.webdriver.chrome.options import Options

# 날짜 포맷을 "2025년 3월 11일(화) 오후 6시"에서 "2025-03-11"로 변환하는 함수
def format_date(date_string):
    match = re.match(r'(\d{4})년 (\d{1,2})월 (\d{1,2})일', date_string)
    if match:
        year = match.group(1)
        month = str(int(match.group(2))).zfill(2)  # 두 자릿수로 월 만들기
        day = str(int(match.group(3))).zfill(2)    # 두 자릿수로 일 만들기
        return f"{year}-{month}-{day}"  # "YYYY-MM-DD" 형식
    return None

def format_apply(date_string):
    match = re.match(r'(\d{4}).(\d{1,2}).(\d{1,2})', date_string)
    if match:
        year = match.group(1)
        month = str(int(match.group(2))).zfill(2)  # 두 자릿수로 월 만들기
        day = str(int(match.group(3))).zfill(2)    # 두 자릿수로 일 만들기
        return f"{year}-{month}-{day}"  # "YYYY-MM-DD" 형식
    return None

# 현재 시간 출력
current_time = datetime.now()
today = current_time.strftime("%Y-%m-%d")

# 초기 설정
pd_list =[]
div_list = []

# 임시 카운트 변수
num = 0

# json 파일 읽기
with open("concert.json", "r", encoding="utf-8") as file:
    read_data = json.load(file)

# 크롬 열기
def start_driver():
    options = Options()
    options.add_argument('--headless')  # 헤드리스 모드
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = wb.Chrome(options=options)
    return driver

driver = start_driver()  # 최초 드라이버 인스턴스 생성
url = "https://ticket.interpark.com/webzine/paper/TPNoticeList.asp?tid1=in_scroll&tid2=ticketopen&tid3=board_main&tid4=board_main"
driver.get(url)

# 대기 시간
time.sleep(1)

# iframe으로 전환 
iframe = driver.find_element(By.ID, 'iFrmNotice')
driver.switch_to.frame(iframe)

# 구분 및 첫번째 페이지 링크 가져오기
first_pg = driver.find_elements(By.CSS_SELECTOR, " tbody a")
div = driver.find_elements(By.CLASS_NAME, "type")

# 구분 리스트에 등록
for i in div:
    if div.index(i) != 0: 
        div_list.append(i.text)

# 대기 시간
time.sleep(1)

# 첫 페이지 클릭 및 iframe 해제
if div_list[0] != "HOT":
    first_pg[0].click()
else:
    first_pg[1].click()
    div_list.remove("HOT")

url = driver.current_url
driver.switch_to.default_content()

# 모든 <a> 태그를 찾기
while True:
    try:
        # 공연 이름, 등록일, 티켓 예매 날짜
        concert_name = driver.find_elements(By.CSS_SELECTOR, "h3")
        w_regist_date = driver.find_elements(By.CLASS_NAME, "date")
        w_ticket_date = driver.find_elements(By.CLASS_NAME, "open")
        
        # 데이터 가공
        concert_del = concert_name[0].text.replace("단독판매", "")
        concert = concert_del.replace("상대우위","")
        
        ticket_date = w_ticket_date[0].text.split("\n")
        ticket = ticket_date[1]
        regist = w_regist_date[0].text[6:]
        
        # 링크
        search_box = driver.find_element(By.TAG_NAME, "input")
        search_box.send_keys(concert)
        search_box.send_keys(Keys.ENTER)
        
        time.sleep(2)  # 페이지 로딩 대기

        try:
            # 공연 링크 찾기
            new_page = driver.find_element(By.CLASS_NAME, "TicketItem_goodsName__Ju76j")
            new_page.click()
        
            # 새 창으로 전환
            current_window = driver.current_window_handle  # 현재 창 핸들 저장
            all_windows = driver.window_handles  # 모든 창의 핸들 리스트
        
            # 새 창으로 전환
            for window in all_windows:
                if window != current_window:  # 현재 창이 아닌 새 창으로 전환
                    driver.switch_to.window(window)
                    break
        
            # 새 창에서 링크 가져오기
            link = driver.current_url
        
            # 새 창 닫기
            driver.close()
        
            # 원래 창으로 돌아가기
            driver.switch_to.window(current_window)
        
            # 대기 시간 및 이후 작업
            time.sleep(1)
        
            driver.back()
        
        except Exception as e:
            print(f"새 창에서 링크 찾기: {num+1}")
            time.sleep(1)
            driver.back()
            link = driver.current_url

        # 페이지 처리 후, 다음 페이지로 이동
        try:
            next_pg = driver.find_element(By.CSS_SELECTOR, "li.next em > a")
            next_pg.click()  # 다음 페이지로 이동
        except Exception as e:
            print(f"다음 페이지로 이동 중 오류 발생: {e}")
            break  # 더 이상 페이지가 없다면 종료
        
        # 리스트 추가
        name_exists = any(item['이름'] == concert for item in read_data)
        
        if not name_exists:
            read_data.append({
                "이름": concert, 
                "구분": div_list[num], 
                "예매날짜": format_date(ticket), 
                "등록일": format_apply(regist), 
                "checked": False
            })
            with open('concert.json', 'w', encoding='utf-8') as file:
                json.dump(read_data, file, ensure_ascii=False, indent=4)
            print(f"새로운 데이터가 추가되었습니다: {read_data}")
        
        # 대기 시간
        time.sleep(2)
        
        num += 1
        if num == 18:
            break

    except Exception as e:
        print(f"오류 발생 (전체 루프): {num+1}")
        driver.quit()
        driver = start_driver()  # 드라이버 재시작
        driver.get(url)
        time.sleep(1)

print("웹 크롤링 완료")

# 구글 SMTP 서버 주소와 포트
smtp_server = "smtp.gmail.com"
smtp_port = 587

# 발신자 이메일 (Gmail)과 수신자 이메일 (네이버 메일)
sender_email = "EMAIL_ADDRESS"  # 구글 이메일
receiver_email = "YOUR_ADDRESS"  # 네이버 이메일
password = "EMAIL_PASSWORD"  # Gmail 2단계 인증을 위한 앱 비밀번호

# 이메일 제목과 내용 설정
subject = "오늘의 콘서트 "

# 이메일 본문에 json 파일 내용 넣기
with open('concert.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
print(data)
body= "오늘 콘서트 행사는 \n"
for e in data:
    if e['등록일'] == today:
        body += f"제목 : {e['이름']}\n 예매일자 : {e['예매날짜']}\n 링크 : {e['링크']}\n\n " 

# MIME 객체로 이메일 구성
msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = subject
msg.attach(MIMEText(body, 'plain'))

# SMTP 서버와 연결하고 이메일 보내기
try:
    # SMTP 서버에 연결
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()  # TLS 암호화 사용
    
    # 로그인
    server.login(sender_email, password)
    
    # 이메일 전송
    text = msg.as_string()
    server.sendmail(sender_email, receiver_email, text)
    
    print("이메일이 성공적으로 전송되었습니다!")
    
except Exception as e:
    print(f"이메일 전송 실패: {e}")
    
finally:
    server.quit()  # 서버 종료
