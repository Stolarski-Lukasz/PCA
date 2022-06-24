FROM python:3.6.8-alpine3.9
LABEL maintainer="Łukasz Stolarski"

WORKDIR /app

COPY . .
RUN apk add ffmpeg
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
