FROM python:3.8-rc-slim

RUN apt update -y && apt install -y build-essential python3-dev libpq-dev gcc

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY ./ /app/

WORKDIR /app
EXPOSE 5000
