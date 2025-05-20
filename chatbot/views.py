# views.py
from django.shortcuts import render
from django.http      import JsonResponse
from django.utils     import timezone

from .read_google_sheet import read_all_sheets   # Google-Sheets 읽어오는 함수

def home(request):
    current_time = timezone.now()

    # ── 1. 구글 시트 전체 읽기
    sheet_data_raw = read_all_sheets()

    # ── 2. '도서관남은자리' 탭만 필터링
    target_name = "도서관남은자리"
    sheet_data  = [(title, rows) for title, rows in sheet_data_raw if title == target_name]


    #target_name = "상록원3층_요일별식단_테이블파싱"
    #sheet_data  = [(title, rows) for title, rows in sheet_data_raw if title == target_name]


    # ── 3. 업데이트 시간 분리
    latest_update_time = None
    if sheet_data and sheet_data[0][1] and sheet_data[0][1][-1][0] == "업데이트 시간":
        latest_update_time = sheet_data[0][1][-1][1]
        sheet_data[0][1].pop()           # 시트 표에서 '업데이트 시간' 행 제거

    return render(request, "chatbot/home.html", {
        "current_time"      : current_time,
        "sheet_data"        : sheet_data,          # 도서관 좌석 현황 한 개만
        "latest_update_time": latest_update_time,  # 마지막 갱신 시각
    })











# ── (AJAX 질문/답변 기능 유지) ──────────────────────────────
def ask(request):
    if request.method == "POST":
        question = request.POST.get("question")
        answer   = f"'{question}'에 대한 답변입니다."
        return JsonResponse({"answer": answer})
