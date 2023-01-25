FROM python:3.7-slim-buster

RUN mkdir /app
ADD . /app
WORKDIR /app

ENV DEBUG "True"
ENV PYTHONUNBUFFERED '1'
ENV LCA_APP_ENV 'production'  
ENV GOOGLE_APPLICATION_CREDENTIALS './config/gcp/lca-prod-key.json'
ENV PORT 8080

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN pip3 install lexnlp  
RUN python3 -m spacy download en_core_web_md
#RUN python3 -m nltk.downloader punkt

EXPOSE 8080
CMD ["python3", "app-run.py"]

