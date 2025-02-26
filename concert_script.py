print("시작", flush=True)
try:
    import os
    from selenium import webdriver as wb
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By
    from datetime import datetime
    import time
    import json
    import re
    from selenium.webdriver.chrome.options import Options
    print("import 완료?", flush=True)
    
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
    
    # 현재 디렉토리에서 concert.json 파일 경로를 동적으로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))  # 현재 파일의 절대 경로
    json_file_path = os.path.join(current_dir, 'static', 'concert.json')  # static 폴더 내의 concert.json 파일
    print(" 현재 디렉토리에서 concert.json 파일 경로를 동적으로 설정", flush=True)
    # json 파일 읽기
    with open(json_file_path, "r", encoding="utf-8") as file:
        read_data = json.load(file)
    print("json 파일 완료")
    
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
    print("크롬 열기", flush=True)
    
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
    print("click", flush=True)
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
    print("페이지 들어가기", flush=True)
    # 모든 <a> 태그를 찾기
    while True:
        print(num,"작업중", flush=True)
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
            
            time.sleep(1)  # 페이지 로딩 대기
    
            try:
                # class가 'btn'인 <a> 태그 찾기
                a_tag = driver.find_element(By.CLASS_NAME, 'btn')

                # href 속성 가져오기
                link = a_tag.get_attribute('href')
            
            except Exception as e:
                print(f"새 창에서 링크 찾기: {num+1}")
                link = driver.current_url
            
            time.sleep(1)
            
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
                    "링크": link,
                    "checked": False
                })
                with open(json_file_path, 'w', encoding='utf-8') as file:
                    json.dump(read_data, file, ensure_ascii=False, indent=4)
                print(f"새로운 데이터가 추가되었습니다: {read_data}")
            
            # 대기 시간
            time.sleep(2)
            
            num += 1
            if num == 18:
                break
    
        except Exception as e:
            print(f"오류 발생 (다시 실행 중): {num+1}")
            # 스크린샷 찍기
            driver.save_screenshot('screenshot.png')
            driver.close()
            driver = start_driver()  # 드라이버 재시작
            driver.get(url)
            time.sleep(1)
    
    print("웹 크롤링 완료")
    driver.close()
except Exception as e:
    print(f"예외 발생: {e}")
