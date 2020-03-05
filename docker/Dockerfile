FROM python:3.8.2-slim-buster
COPY requirements.txt .
COPY database/db-config.yaml .
COPY database/db_reader.py .
COPY scrapping/ .
RUN pip install -r requirements.txt
CMD ["python", "being_scrapping.py"]