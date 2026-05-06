FROM python:3.10-slim

# نصب Nginx و ابزارها
RUN apt-get update && \
    apt-get install -y wget unzip nginx && \
    mkdir -p /var/log/nginx && \
    mkdir -p /var/lib/nginx/body

# دانلود Xray
RUN wget https://github.com/XTLS/Xray-core/releases/download/v1.8.4/Xray-linux-64.zip && \
    unzip Xray-linux-64.zip && \
    chmod +x xray && \
    rm Xray-linux-64.zip

COPY app.py .

# باز کردن پورت ۳۰۰۰ برای رانفلر
EXPOSE 3000

CMD ["python", "app.py"]
