FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py index.html desk.html data.py seed_data.py ./
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 main:app
