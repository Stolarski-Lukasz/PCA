FROM python:3.6.8-alpine3.9
LABEL maintainer="Łukasz Stolarski"

COPY . .
RUN apk add ffmpeg
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
