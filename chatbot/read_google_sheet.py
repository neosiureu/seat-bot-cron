# chatbot/read_google_sheet.py
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account

SERVICE_ACCOUNT_FILE = 'calm-axis-457509-u0-36793e7c962b.json'
 # Django 루트에 위치시킴
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
# SPREADSHEET_ID = '1oEHz1980O2zAWlug19huO4HJASD-YMWQkIHqerqfgRE' # 졸업요건 모두 출력
# SPREADSHEET_ID = '1Dbat_6AEVQwL2uCyWKIoS-lsGD6DYt5WO9wfsjxvOs8' # 전화번호 모두 출력
# SPREADSHEET_ID = '1oEHz1980O2zAWlug19huO4HJASD-YMWQkIHqerqfgRE' # 과목상세설명 모두 출력
# SPREADSHEET_ID = '1j9klCxdjdsbdHDB-d2z1WDVxeu4mtPHOu-tb8XC156I' # 강의실 위치 모두 출력




#SPREADSHEET_ID  = '1XLk3MqoQv2142weWKsXM3jnatm3zxo7S2J8F81HGwoo'
# 상록원 2층 (동적으로 업데이트될 DB)




#SPREADSHEET_ID  = '1rV4I8E2IB-08477zmApTCh7eaItJK4YvHutkZ5UbP4w'
# 상록원 3층 (동적으로 업데이트될 DB)




SPREADSHEET_ID = '1RZWsHqvxNKqfkHIKpzJ09Ij38IyyZdj58Je8yyb-dN0'
# 도서관 남은자리 (동적으로 업데이트될 DB)




def read_all_sheets():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    service = build('sheets', 'v4', credentials=creds)
    spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    sheets = spreadsheet.get('sheets', [])
    
    result = []

    for sheet in sheets:
        title = sheet['properties']['title']
        RANGE_NAME = f'{title}!A1:Z1000'
        try:
            values = service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME
            ).execute().get('values', [])

            result.append((title, values))  # (시트 이름, 행 목록)
        except Exception as e:
            result.append((title, [['Error reading data:', str(e)]]))
            
    
    return result  # [(시트명, [[행1], [행2], ...]), ...]





# 아래 함수는 기존 내용을 clear 후 새로운 내용을 덮어씀 => 식당메뉴 혹은 도서관 남은자리 자료와 같은 동적 DB를 생성할 때 쓰인다.

def overwrite_google_sheet(sheet_name: str, values: list[list[str]]) -> None:
    """
    지정한 시트(sheet_name)를 통째로 비우고(values.clear) 새 values 를 A1부터 채워 넣는다.
    마지막에 '업데이트 시간' 행을 자동 삽입한다.
    """
    creds    = service_account.Credentials.from_service_account_file(
                  SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service  = build('sheets', 'v4', credentials=creds)

    # ① 전부 지울 때는 시트 이름만 넘긴다
    sheet_range_for_clear  = sheet_name            # ex) "상록원3층_요일별식단_테이블파싱"
    # ② A1부터 기록할 때는 "!A1"을 붙인다
    sheet_range_for_write  = f"{sheet_name}!A1"

    # 업데이트 시간 행 추가
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    values.append(["업데이트 시간", now_str])

    # ── 1. 시트 전체 Clear ───────────────────────────────
    service.spreadsheets().values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range=sheet_range_for_clear
    ).execute()

    # ── 2. 새 데이터 Write ───────────────────────────────
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=sheet_range_for_write,
        valueInputOption='RAW',
        body={'values': values}
    ).execute()
