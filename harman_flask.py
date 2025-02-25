import webbrowser
import threading
import subprocess
import logging
from flask import Flask, render_template, request, jsonify
import json
import os
import requests

# GitHub raw URL
url = "https://raw.githubusercontent.com/taemin-ctrl/project/main/static/concert.json"

# 로컬에 저장할 파일 경로
json_file_path = 'static/concert.json'

# 파일 다운로드
response = requests.get(url)

# 요청이 성공한 경우 파일 저장
if response.status_code == 200:
    with open(json_file_path, 'wb') as file:
        file.write(response.content)
    print(f"파일이 {json_file_path}에 성공적으로 저장되었습니다.")
else:
    print(f"파일을 다운로드하는데 실패했습니다. 상태 코드: {response.status_code}")

# Flask 로그 설정
logging.basicConfig(level=logging.DEBUG)  # 모든 로그 레벨을 디버그로 설정
logger = logging.getLogger(__name__)

app = Flask(__name__)




@app.route("/")
def index():
    logger.debug("Rendering the index page.")
    return render_template("cal.html")

# 기존 이벤트 불러오기
@app.route("/get_events")
def get_events():
    logger.debug("Fetching events.")
    try:
        with open(json_file_path, 'r', encoding='UTF-8') as file:
            events = json.load(file)

        return jsonify(events)
    
    except FileNotFoundError:
        logger.error(f"File not found: {json_file_path}")
        return jsonify({"error": "File not found"}), 404
    
    except Exception as e:
        logger.error(f"Error while fetching events: {e}")
        return jsonify({"error": f"An error occurred: {e}"}), 500

# 체크 상태 저장 → concert.json에 반영
@app.route("/save_checked_state", methods=["POST"])
def save_checked_state():
    logger.debug("Saving checked state.")
    try:
        updated_events = request.get_json()

        with open(json_file_path, 'r', encoding='UTF-8') as file:
            original_data = json.load(file)

        # 이름 기준으로 checked 상태 업데이트
        for orig_event in original_data:
            for updated_event in updated_events:
                if orig_event["﻿이름"] == updated_event["name"]:  # BOM 문자 주의
                    orig_event["checked"] = updated_event["checked"]
                    orig_event["actived"] = updated_event["actived"]

        # 업데이트된 데이터 저장
        with open(json_file_path, 'w', encoding='UTF-8') as file:
            json.dump(original_data, file, ensure_ascii=False, indent=4)

        logger.info("Checked state saved successfully.")
        return jsonify({"message": "체크 상태가 저장되었습니다!"})
    
    except Exception as e:
        logger.error(f"Error while saving checked state: {e}")
        return jsonify({"error": str(e)}), 500



def open_browser():
    webbrowser.open("http://localhost:5000") # 서버 주소

if __name__ == "__main__":
    threading.Timer(0.5, open_browser).start()
    logger.info("Starting the Flask application.")
    app.run(host="localhost", debug=False)


# pyinstaller --onefile --add-data "templates/cal.html;templates" --add-data "static/js/script.js;static/js" --add-data "static/css/style.css;static/css" harman_flask.py
# json 빼고 포함해서 exe 파일 생성