FROM python:3.7-slim-buster

RUN mkdir /app
ADD . /app
WORKDIR /app
ENV DEBUG "True"
ENV PYTHONUNBUFFERED '1'
ENV REQUIREMENTS 'requirements.txt' 
ENV PORT 8080 

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN python3 -m spacy download en_core_web_md

EXPOSE 8080
CMD ["python3", "app-run.py"]

