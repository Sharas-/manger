FROM python:3.7.3-alpine3.9 
COPY requirements.txt .
RUN pip install -r requirements.txt
WORKDIR /srv
COPY code/ ./
EXPOSE 8000
ENTRYPOINT ["gunicorn", "--bind=0.0.0.0:8000", "webapi.app"]
CMD ["--access-logfile=-"]
