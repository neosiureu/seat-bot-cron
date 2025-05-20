FROM selenium/standalone-chrome:136.0

USER root
RUN apt-get update && apt-get install -y unzip && rm -rf /var/lib/apt/lists/*

# GCP 서비스 계정 키
COPY calm-axis-457509-u0-36793e7c962b.json /app/
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/calm-axis-457509-u0-36793e7c962b.json

# Python 의존성
COPY requirements.txt /app/
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드
COPY chatbot /app/chatbot
ENV PYTHONUNBUFFERED=1

USER seluser
CMD ["python", "-m", "chatbot.library_seat"]
