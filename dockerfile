FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
  COPY . .

CMD ["sh", "-c", "python manage.py migrate && python manage.py loaddata db_dump.json && python manage.py runserver 0.0.0.0:8000"]