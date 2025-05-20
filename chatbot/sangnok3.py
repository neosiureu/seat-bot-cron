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

from chatbot.read_google_sheet import overwrite_google_sheet   # 스프레드시트 쓰기

# ── ① 크롬 무Headless 설정 ───────────────────────────
CHROME_PATH      = r"C:\chrome-win64\chrome.exe"
CHROMEDRIVER_PATH= r"C:\chromedriver-win64\chromedriver.exe"

opts = Options()
opts.binary_location = CHROME_PATH
opts.add_argument("--headless"); opts.add_argument("--disable-gpu"); opts.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=opts)
wait   = WebDriverWait(driver, 10)

# ── ② 이번주 (오늘이 일요일이면 다음주) 월요일 자정(KST) 기준 sday 계산 ──
today = datetime.now()
delta_to_mon = (-today.weekday()) % 7          # 월=0, … , 일=1  (일요일 → +1 해서 다음주 월)
monday_dt = (today + timedelta(days=delta_to_mon)).replace(hour=0,minute=0,second=0,microsecond=0)

KST = pytz.timezone("Asia/Seoul")
days = {}
for i, name in enumerate(["월","화","수","목","금","토"]):
    dt   = KST.localize(monday_dt + timedelta(days=i))
    days[name] = str(int(dt.timestamp()))

# ── ③ 식단 크롤링 & 정제 ─────────────────────────────
data = [["요일","sday","구분","중식","석식"]]
code = "5"   # 상록원 3층

for yoil, sday in days.items():
    url = f"https://dgucoop.dongguk.edu/mobile/menu.html?code={code}&sday={sday}"
    driver.get(url)
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"table")))
    except:                                   # 테이블 없으면 패스
        print(f"[ERROR] {yoil}요일 테이블 로딩 실패");  continue

    soup  = BeautifulSoup(driver.page_source,"html.parser")
    table = soup.find("table");  rows = table.find_all("tr")
    last_gu = None

    for tr in rows:
        tds = tr.find_all("td");  # 3열 고정
        if len(tds) < 3:  continue

        raw = [td.get_text("\n",strip=True) for td in tds]
        if raw == ["구분","중식","석식"]:      # 헤더 skip
            continue
        gu,lunch,dinner = raw

        if not any((gu,lunch,dinner)):        # 완전빈행 skip
            continue
        if gu and gu != "구분":               # 새 구분 감지
            last_gu = gu
        else:                                 # 구분 칸이 비면 이전 값 이어쓰기
            gu = last_gu

        data.append([yoil, sday, gu, lunch, dinner])

    sleep(0.8)                                # 서버부담 완화

driver.quit()

# ── ④ 스프레드시트 업데이트 ─────────────────────────
overwrite_google_sheet("상록원3층_요일별식단_테이블파싱", data)
print(" 스프레드시트 최신 식단 반영 완료")
