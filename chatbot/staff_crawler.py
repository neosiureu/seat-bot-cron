# ── 교직원 전화번호 크롤링 → Google Sheets 덮어쓰기 ──────────────
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options  import Options
from selenium.webdriver.common.by       import By
from selenium.webdriver.support.ui      import WebDriverWait
from selenium.webdriver.support         import expected_conditions as EC
from bs4        import BeautifulSoup
from datetime   import datetime
from time       import sleep

# Google Sheets API   (read_google_sheet.py 그대로 사용)
from chatbot.read_google_sheet import overwrite_google_sheet

# ── 0. 상수 ────────────────────────────────────────────────────────
SPREAD_SHEET_NAME = "교직원전화번호"               # 탭 이름
STAFF_URL         = "https://www.dongguk.edu/staff/list"
CHROME_PATH       = r"C:\chrome-win64\chrome.exe"
CHROMEDRIVER_PATH = r"C:\chromedriver-win64\chromedriver.exe"

# ── 1. 셀레니움 드라이버 ───────────────────────────────────────────
opts = Options()
opts.binary_location = CHROME_PATH
opts.add_argument("--headless"); opts.add_argument("--disable-gpu")
opts.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=opts)
wait   = WebDriverWait(driver, 10)

# ── 2. 검색 함수 ──────────────────────────────────────────────────
def search_number(keyword: str) -> list[list[str]]:
    """키워드(0~9) 하나를 검색해 테이블에서 모든 행을 리스트로 반환한다"""
    driver.get(STAFF_URL)

    # ① 두 번째 드롭다운을 '전화번호'로 바꾸기
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
            "div.search-area select[name='searchCondition']")))
    cond_sel = driver.find_element(By.CSS_SELECTOR, 
            "div.search-area select[name='searchCondition']")
    driver.execute_script("arguments[0].value='phone'; arguments[0].dispatchEvent(new Event('change'))", cond_sel)

    # ② 검색어 입력 후 엔터
    inp = driver.find_element(By.CSS_SELECTOR, "input[name='keyword']")
    inp.clear(); inp.send_keys(keyword)
    inp.submit()

    # ③ 결과 테이블이 로드될 때까지 대기
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tbody tr")))
    sleep(0.5)          # JS 렌더링 딜레이 대비

    rows: list[list[str]] = []
    while True:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        for tr in soup.select("tbody tr"):
            tds = [td.get_text(strip=True) for td in tr.select("td")]
            if len(tds) == 4:          # 부서/직급/이름/전화번호
                rows.append(tds)

        # ④ 다음 페이지가 있으면 클릭, 없으면 종료
        nxt = soup.select_one("a.next")   # <a class="next"> 또는 disabled
        if not nxt or "disabled" in nxt.get("class", []):
            break
        driver.find_element(By.LINK_TEXT, nxt.get_text(strip=True)).click()
        wait.until(EC.staleness_of(tr))   # 페이지 전환 대기

    return rows

# ── 3. 0~9까지 반복 검색 후 병합 ─────────────────────────────────
all_rows = []
for d in map(str, range(10)):
    print(f" ☞ '{d}' 검색 중…")
    all_rows += search_number(d)

print(f"  >> 총 {len(all_rows):,}행 수집.")

# ── 4. 중복 제거 (전화번호가 같으면 동일 행으로 간주) ─────────────
seen = set()
uniq_rows = []
for r in all_rows:
    phone = r[3]
    if phone not in seen:
        seen.add(phone)
        uniq_rows.append(r)

print(f"  >> 중복 제거 후 {len(uniq_rows):,}행.")

# ── 5. 헤더 추가 & 시트 덮어쓰기 ──────────────────────────────────
header = ["부서(학과)명", "직급", "이름", "전화번호", "크롤링시각"]
crawl_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
final = [header] + [row + [crawl_time] for row in uniq_rows]

overwrite_google_sheet(SPREAD_SHEET_NAME, final)
print(f"교직원 전화번호 업데이트 완료  ({crawl_time})")

driver.quit()
