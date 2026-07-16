FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

RUN useradd -m -u 1000 bridgeuser
USER bridgeuser

EXPOSE 8765
CMD ["python", "server.py"]
