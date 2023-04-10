FROM python:3.9-slim-buster

WORKDIR /app

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

EXPOSE 5000

COPY . .

# CMD ["python3", "producer.py"]
CMD ["flask", "run"]
