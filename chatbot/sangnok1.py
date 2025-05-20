from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz

def get_menu_list():
    CHROME_PATH = r"C:\chrome-win64\chrome.exe"
    CHROMEDRIVER_PATH = r"C:\chromedriver-win64\chromedriver.exe"

    options = Options()
    options.binary_location = CHROME_PATH
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    # 서버 시간 기준으로 이번 주 월~금 날짜 생성
    now = datetime.now(pytz.timezone('Asia/Seoul'))
    start_of_week = now - timedelta(days=now.weekday())
    weekdays = ['월', '화', '수', '목', '금']

    days = []
    for i in range(5):
        day = start_of_week + timedelta(days=i)
        sday = int(day.replace(hour=0, minute=0, second=0).timestamp())
        days.append((weekdays[i], str(sday)))

    result_list = []

    for day_name, sday in days:
        url = f"https://dgucoop.dongguk.edu/mobile/menu.html?code=7&sday={sday}"
        driver.get(url)

        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "td[style*='border:1px solid']"))
            )
            soup = BeautifulSoup(driver.page_source, "html.parser")
            menus = soup.find_all("td", style=lambda v: v and "border:1px solid" in v)

            for td in menus:
                raw_lines = td.decode_contents().split("<br>")
                lines = [BeautifulSoup(line.strip(), "html.parser").text for line in raw_lines if line.strip()]
                menu_text = "\n".join(lines)
                if not menu_text.strip() or "메뉴" in menu_text:
                    continue
                result_list.append(f"[{day_name}요일] {menu_text}")

        except Exception as e:
            result_list.append(f"[{day_name}요일] 로딩 실패: {e}")

    driver.quit()
    return result_list
