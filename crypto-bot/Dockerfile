FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Previously ran as root by default -- unnecessary given this process only
# needs outbound HTTPS to Jupiter/Solana RPC, no privileged access.
RUN useradd -m -u 1000 botuser
USER botuser

CMD ["python", "bot.py"]
