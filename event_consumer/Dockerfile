FROM python:3.12-slim
RUN apt-get update && apt-get install -y dnsutils

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "consumer.py"]
