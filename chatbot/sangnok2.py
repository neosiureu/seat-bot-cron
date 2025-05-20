# sangnok2.py ─ 상록원 2층 식단 크롤링 → Google Sheets 덮어쓰기
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options  import Options
from selenium.webdriver.common.by       import By
from selenium.webdriver.support.ui      import WebDriverWait
from selenium.webdriver.support         import expected_conditions as EC
from bs4        import BeautifulSoup
from datetime   import datetime, timedelta
from time       import sleep
import pytz

from chatbot.read_google_sheet import overwrite_google_sheet

# ── 1. 셀레니움 드라이버 설정 ──────────────────────────
CHROME_PATH       = r"C:\chrome-win64\chrome.exe"
CHROMEDRIVER_PATH = r"C:\chromedriver-win64\chromedriver.exe"

opts = Options()
opts.binary_location = CHROME_PATH
opts.add_argument("--headless"); opts.add_argument("--disable-gpu"); opts.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=opts)
wait   = WebDriverWait(driver, 10)

# ── 2. 이번 주(또는 다음 주) 월요일 09:00(KST) 기준 sday 계산 ──
today = datetime.now()
delta_to_mon = (-today.weekday()) % 7          # 월=0 … 일=1 → 일요일이면 다음주 적용
monday_dt = (today + timedelta(days=delta_to_mon)).replace(hour=9, minute=0, second=0, microsecond=0)

KST = pytz.timezone("Asia/Seoul")
days = {}
for i, name in enumerate(["월", "화", "수", "목", "금", "토"]):
    dt   = KST.localize(monday_dt + timedelta(days=i))
    days[name] = str(int(dt.timestamp()))

# ── 3. 식단 크롤링 ─────────────────────────────────────
data = [["요일", "sday", "구분", "중식", "석식"]]
code = "1"   # 2층 코드

for yoil, sday in days.items():
    url = f"https://dgucoop.dongguk.edu/mobile/menu.html?code={code}&sday={sday}"
    driver.get(url)

    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))
    except:
        print(f"[ERROR] {yoil}요일 테이블 로딩 실패");  continue

    soup  = BeautifulSoup(driver.page_source, "html.parser")
    table = soup.find("table");  rows = table.find_all("tr")
    last_gu = None

    for tr in rows:
        tds = tr.find_all("td")
        if len(tds) < 3:  continue

        gu_txt, lunch, dinner = [td.get_text("\n", strip=True) for td in tds]

        # 헤더 skip
        if (gu_txt, lunch, dinner) == ("구분", "중식", "석식"):
            continue
        # 완전 빈행 skip
        if not any((gu_txt.strip(), lunch.strip(), dinner.strip())):
            continue

        # 구분 처리
        if gu_txt and gu_txt not in {"구분"}:
            last_gu = gu_txt
        gu = last_gu if gu_txt in {"", "구분"} else gu_txt

        print(f"[{yoil}] 구분={gu}, 중식={lunch}, 석식={dinner}")
        data.append([yoil, sday, gu, lunch, dinner])

    sleep(0.8)   # 서버 부하 완화

driver.quit()

# ── 4. Google Sheets 덮어쓰기 ─────────────────────────
overwrite_google_sheet("상록원2층_요일별식단_테이블파싱", data)
print(" 상록원 2층 스프레드시트 최신 식단 반영 완료")
