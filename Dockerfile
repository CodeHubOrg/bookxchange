FROM python:3.6

ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY manage.py requirements.txt /app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt


COPY . /app/

EXPOSE 8000
