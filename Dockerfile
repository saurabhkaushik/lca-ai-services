FROM python:3.7-slim-buster

RUN mkdir /app
ADD . /app
WORKDIR /app
ENV GOOGLE_APPLICATION_CREDENTIALS='store/sk-exp-009-35eadef25aaa.json'
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN python3 -m spacy download en_core_web_sm
#RUN sh setup.sh

EXPOSE 8080
CMD ["python3", "app-run.py"]