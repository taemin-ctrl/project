    let events = [];

    fetch('..//static//concert.json')
        .then(response => response.json())
        .then(data => {
            // JSON 데이터를 events 배열에 추가
            data.forEach(concert => {
                events.push({
                    id: Date.now() + Math.random(), // 고유 ID 생성
                    type: concert["구분"],
                    name: concert["﻿이름"],
                    date: concert["예매날짜"],
                    apply: concert["등록일"],
                    link: concert["링크"],
                    checked: false,
                    actived: concert["actived"]
                });
            });

            // 이벤트 목록과 달력 업데이트
            updateEventList();
            generateCalendar();
        })
        .catch(error => console.error('데이터를 불러오는 중 오류 발생:', error));


    let currentDate = new Date();
    const MAX_EVENTS = 20;
    const colorMap = {
    '뮤지컬': '#2196F3',
    '콘서트': '#4CAF50',
    '연극': '#9C27B0',
    '클래식/무용': '#dfa42f',
    '아동/가족': '#ff0396',
    '스포츠': '#009688',
    '레저': '#2b1a01',
    '전시/행사': 'hsl(242, 100%, 28%)'
    };
    // 달력 생성
    function generateCalendar() {
    const calendarBody = document.getElementById('calendarBody');
    calendarBody.innerHTML = '';

    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    document.getElementById('currentMonth').textContent = 
        `${year}년 ${month + 1}월`;

    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const prevMonthLastDay = new Date(year, month, 0).getDate();
    const startDay = firstDay.getDay();

    let date = 1;
    let html = '';

    for (let i = 0; i < 6; i++) {
        html += '<tr>';
        for (let j = 0; j < 7; j++) {
            const dayClass = j === 0 ? 'sunday' : (j === 6 ? 'saturday' : '');  // 일요일은 sunday, 토요일은 saturday로 구분
            let cellClass ='calendar-day' ;

            if (i === 0 && j < startDay) {
                // 이전 달 날짜
                const prevDate = prevMonthLastDay - (startDay - j - 1);
                cellClass += ' other-month'; // other-month 클래스 추가
                html += `
                    <td class="${cellClass} ${dayClass}" 
                        data-date="${year}-${String(month).padStart(2,'0')}-${String(prevDate).padStart(2,'0')}">
                        <div class="date-number">${prevDate}</div>
                    </td>`;
            }
            else if (date > lastDay.getDate()) {
                // 다음 달 날짜
                const nextDate = date - lastDay.getDate();
                cellClass += ' other-month'; // other-month 클래스 추가
                html += `
                    <td class="${cellClass} ${dayClass}" 
                        data-date="${year}-${String(month+2).padStart(2,'0')}-${String(nextDate).padStart(2,'0')}">
                        <div class="date-number">${nextDate}</div>
                    </td>`;
                date++;
            } 
            else {
                // 현재 달 날짜
                html += `
                    <td class="${cellClass} ${dayClass}" 
                        data-date="${year}-${String(month+1).padStart(2,'0')}-${String(date).padStart(2,'0')}">
                        <div class="date-number">${date}</div>
                    </td>`;
                date++;
            }
        }
        html += '</tr>';
        if (date > lastDay.getDate()) break;
    }

    calendarBody.innerHTML = html;
    renderEvents();
    }

    function showEventDetails(event) {
        document.getElementById('popupEventName').textContent = event.name;
        document.getElementById('popupEventType').textContent = event.type;
        document.getElementById('popupEventDate').textContent = event.date;
        document.getElementById('popupEventApply').textContent = event.apply;
        document.getElementById('popupEventLink').textContent = event.link;
        const linkElement = document.getElementById('popupEventLink');
        if (event.link && event.link.trim() !== "") {
            linkElement.innerHTML = `<a href="${event.link}" target="_blank" style="color: #007BFF; text-decoration: underline;">${event.link}</a>`;
        } else {
            linkElement.innerHTML = "링크 없음";
        }
        document.getElementById('eventDetailPopup').style.display = 'block'; // 모달 띄우기
    }

    // 팝업 닫기
    function closePopup() {
        document.getElementById('eventDetailPopup').style.display = 'none'; // 모달 숨기기
    }


    function renderEvents() {
        document.querySelectorAll('.calendar-day').forEach(cell => {
            cell.querySelectorAll('.event-badge').forEach(badge => badge.remove());
    
            const date = cell.dataset.date;
    
            // actived가 true인 이벤트만 필터링
            events.filter(event => event.checked && event.date === date && event.actived)
                .forEach(event => {
                    const badge = document.createElement('div');
                    badge.className = 'event-badge';
                    badge.setAttribute('data-type', event.type);
                    badge.style.backgroundColor = colorMap[event.type] || '#cccccc';
                    badge.textContent = `${event.type} - ${event.name}`;
                    badge.onclick = () => showEventDetails(event);
    
                    cell.appendChild(badge);
                });
        });
    }

    // 이벤트 추가
    function addEvent() {
        const newEvent = {
            id: Date.now(),
            type: document.getElementById('eventType').value,
            name: document.getElementById('eventName').value,
            date: document.getElementById('eventDate').value,
            checked: false
        };

        if (!newEvent.type || !newEvent.name || !newEvent.date) {
            alert('모든 필드를 입력해주세요');
            return;
        }

        if (events.length >= MAX_EVENTS) {
            alert('최대 20개까지 추가 가능합니다');
            return;
        }

        events.push(newEvent);
        updateEventList();
        generateCalendar();
        clearInputs();
    }
    let currentPage = 1; // 현재 페이지 번호
    const eventsPerPage = 10; // 한 페이지에 보여줄 공연 개수

    // 이벤트 목록 업데이트 함수
    function updateEventList(filteredEvents = events) {
        const eventList = document.getElementById('eventList');
        const startIdx = (currentPage - 1) * eventsPerPage;
        const endIdx = currentPage * eventsPerPage;
        const activedEvents = filteredEvents.filter(event => event.actived !== false); // actived가 true인 이벤트만 필터링
    
        const paginatedEvents = activedEvents.slice(startIdx, endIdx);
    
        eventList.innerHTML = paginatedEvents.map(event => `
            <div class="event-item">
                <label>
                    <input type="checkbox" ${event.checked ? 'checked' : ''} onchange="toggleEvent(${event.id})">
                    ${event.date} <${event.type}>${event.name}
                </label>
                <button onclick="deleteEvent(${event.id})">삭제</button>
            </div>
        `).join('');
    
        updatePagination(activedEvents.length); // actived가 true인 이벤트 갯수로 페이지네이션 업데이트
    }


    // 페이지네이션 업데이트
    function updatePagination(totalEvents) {
        const pagination = document.getElementById('pagination');
        const totalPages = Math.ceil(totalEvents / eventsPerPage);
        pagination.innerHTML = '';
        
        for (let i = 1; i <= totalPages; i++) {
            const pageButton = document.createElement('button');
            pageButton.textContent = i;
            pageButton.onclick = () => changePage(i);
            pagination.appendChild(pageButton);
        }
    }

    // 페이지 변경
    function changePage(pageNumber) {
        currentPage = pageNumber;
        applyFilters();
    }

    // 필터 적용 함수 (필터링 후 페이지 변경)
    function applyFilters() {
        const filterApply = document.getElementById('filterApply').value;
        const filterDate = document.getElementById('filterDate').value;
        const filterType = document.getElementById('filterType').value;

        const filteredEvents = events.filter(event => {
            const matchesApply = filterApply ? event.apply === filterApply : true;
            const matchesDate = filterDate ? event.date === filterDate : true;
            const matchesType = filterType ? event.type === filterType : true;
            return matchesApply && matchesDate && matchesType;
        });

        updateEventList(filteredEvents);
    }

    // 현재 달력의 연도와 월을 표시
    function updateCalendarHeader() {
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth() + 1; // 1부터 12까지 표시
        document.getElementById('currentMonth').textContent = `${year}년 ${month}월`;
    }

    // 월 드롭다운 표시 토글
    function toggleMonthSelector() {
        const selector = document.getElementById('monthSelector');
        selector.style.display = selector.style.display === 'none' ? 'block' : 'none';
    }

    // 연도 및 월 드롭다운 값 변경 시 달력 업데이트
    function updateCalendar() {
        const year = document.getElementById('yearSelect').value;
        const month = document.getElementById('monthSelect').value - 1; // 0부터 11까지
        currentDate.setFullYear(year);
        currentDate.setMonth(month);
        generateCalendar();
        updateCalendarHeader();
        toggleMonthSelector(); // 드롭다운 숨기기
    }

    // 연도와 월 옵션 동적 추가
    function populateYearMonthSelectors() {
        const yearSelect = document.getElementById('yearSelect');
        const monthSelect = document.getElementById('monthSelect');
        
        const currentYear = currentDate.getFullYear();
        
        // 연도 옵션 생성
        for (let year = currentYear - 5; year <= currentYear + 5; year++) {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = `${year}년`;
            if (year === currentYear) option.selected = true;
            yearSelect.appendChild(option);
        }

        // 월 옵션 생성
        for (let month = 1; month <= 12; month++) {
            const option = document.createElement('option');
            option.value = month;
            option.textContent = `${month}월`;
            if (month === currentDate.getMonth() + 1) option.selected = true;
            monthSelect.appendChild(option);
        }
    }

    // 초기 실행
    populateYearMonthSelectors();
    updateCalendarHeader();

    // 전체 선택/해제 기능
    function toggleSelectAll() {
        const selectAllButton = document.getElementById('selectAll');
        
        // 모든 이벤트가 선택된 상태인지 확인
        const allChecked = events.every(event => event.checked); // 모든 이벤트가 체크되었으면 true, 아니면 false
        
        // 버튼 텍스트 변경
        selectAllButton.innerText = allChecked ? '전체 선택' : '전체 해제';
        
        // 전체 선택 또는 해제
        events.forEach(event => {
            event.checked = !allChecked; // 모든 이벤트가 체크되었으면 해제, 아니면 선택
        });
        
        updateEventList(); // 이벤트 목록 업데이트
        renderEvents(); // 달력에 이벤트 표시
    }



    function toggleEvent(eventId) {
        const event = events.find(e => e.id === eventId);
        if (event) {
            event.checked = !event.checked;
            updateEventList();
            renderEvents();
        }
    }

    // 이벤트 삭제 (삭제 시 actived 값을 false로 설정)
    function deleteEvent(eventId) {
        const event = events.find(e => e.id === eventId);
        if (event) {
            event.actived = false; // 삭제된 이벤트는 actived 값을 false로 설정
        }

        saveLogic();
        // 이벤트 리스트에서 삭제
        events = events.filter(e => e.id !== eventId);

        updateEventList(); // 업데이트된 이벤트 목록 반영
        generateCalendar(); // 달력 업데이트
    }

    // 날짜 형식 변환
    function formatDate(date) {
        return date.toISOString().split('T')[0];
    }

    // 입력 필드 초기화
    function clearInputs() {
        document.getElementById('eventType').value = '';
        document.getElementById('eventName').value = '';
        document.getElementById('eventDate').value = '';
    }

    // 월 변경
    function changeMonth(offset) {
        currentDate.setMonth(currentDate.getMonth() + offset);
        generateCalendar();
    }

    function saveLogic(){
        fetch('/save_checked_state', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(events) // 전체 이벤트 상태 전송
        })
    }

    // 체크 상태 저장
    function saveCheckState() {
        fetch('/save_checked_state', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(events) // 전체 이벤트 상태 전송
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message || '저장 완료!');
        })
        .catch(error => {
            console.error('저장 실패:', error);
            alert('저장 실패');
        });
    }
    // 체크 상태 불러오기
    function loadCheckState() {
        fetch('/get_events')
            .then(response => response.json())
            .then(data => {
                events = data.map(concert => ({
                    id: Date.now() + Math.random(), // 고유 ID 추가
                    name: concert["﻿이름"],
                    type: concert["구분"],
                    date: concert["예매날짜"],
                    apply: concert["등록일"],
                    link: concert["링크"],
                    checked: concert["checked"] || false,
                    actived: concert["actived"] && true // actived가 true일 때만 로드
                }))

                updateEventList();
                renderEvents();
                alert('불러오기 완료!');
            })
            .catch(error => {
                console.error('불러오기 실패:', error);
                alert('불러오기 실패');
            });
    }

    // 초기 실행
    generateCalendar();
    updateEventList();
