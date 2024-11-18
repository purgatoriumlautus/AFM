#use existing image as base
FROM python:3.12

# Retrieve needed files nad dependencies

WORKDIR /afm

COPY ./requirements.txt requirements.txt

RUN pip insall -r requirements.txt
ENV FLASK_APP=src.app.py

COPY . .



# CMD ["flask", "run","--host=0.0.0.0"]