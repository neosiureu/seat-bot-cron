from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
from chatbot.read_google_sheet import overwrite_google_sheet
from datetime import datetime
from zoneinfo import ZoneInfo

SPREAD_SHEET_NAME = "도서관남은자리"
LIB_MAIN_URL      = "https://lib.dongguk.edu/"

def main():
    # ── 1) Chrome 옵션
    print("▶ [1] Chrome 옵션 설정 중...")
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    print("▶ [1] Chrome 옵션 설정 완료")

    # ── 2) ChromeDriver 직접 호출
    print("▶ [2] ChromeDriver 실행 중...")
    driver = webdriver.Chrome(options=opts)
    print("▶ [2] ChromeDriver 실행 완료")

    # ── 3) 페이지 요청
    print(f"▶ [3] {LIB_MAIN_URL} 요청 중...")
    driver.get(LIB_MAIN_URL)
    print("▶ [3] 페이지 요청 완료")

    # ── 4) 요소 로드 대기
    print("▶ [4] 요소(li.book) 로드 대기 중...")
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "li.book"))
    )
    print("▶ [4] 요소 로드 완료")

    # ── 5) 파싱
    print("▶ [5] 페이지 소스 파싱 중...")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    print("▶ [5] 파싱 완료")

    driver.quit()
    print("▶ 드라이버 종료 완료")

    # ── 6) 데이터 구성
    print("▶ [6] 데이터 생성 중...")
    rows = [["공간", "남은", "사용중", "전체", "크롤링시각"]]
    timestamp = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")
    for li in soup.select("ul#seatUl li.book"):
        room   = li.select_one("h3.type1").get_text(strip=True)
        used   = int(li.select_one("span.num").text.replace(",", "") or 0)
        total  = int(li.select_one("span.total").text.replace(",", "") or 0)
        remain = max(total - used, 0)
        rows.append([room, remain, used, total, timestamp])
    print(f"▶ [6] 데이터 준비 완료: {len(rows)-1}개 항목")

    # ── 7) 구글 시트 업데이트
    print("▶ [7] 구글 시트 업데이트 중...")
    overwrite_google_sheet(SPREAD_SHEET_NAME, rows)
    print("▶ [7] 구글 시트 업데이트 완료")

    print(f"[{timestamp}] 도서관 좌석 현황 업데이트 완료")

if __name__ == "__main__":
    main()
