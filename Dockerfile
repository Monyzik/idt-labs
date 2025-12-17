FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y gcc curl && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


COPY . .
EXPOSE 8000
CMD ["fastapi", "run", "src/main.py", "--port", "8000", "--reload"]


HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ["curl", "-f", "0.0.0.0:8000/api/health"]
