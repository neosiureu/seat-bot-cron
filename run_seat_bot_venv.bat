@echo off
cd /d C:\serverspace\chatbot_project
call venv\Scripts\activate.bat

REM ← 여기부터 추가
set GOOGLE_APPLICATION_CREDENTIALS=C:\serverspace\chatbot_project\calm-axis-457509-u0-36793e7c962b.json
REM ← 여기까지

python -m chatbot.library_seat 