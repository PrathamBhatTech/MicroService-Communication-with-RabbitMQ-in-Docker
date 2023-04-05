FROM python:3.9-slim-buster

WORKDIR /app

COPY . .
RUN pip3 install -r requirements.txt

EXPOSE 9004

CMD ["python3", "consumer.py"]
