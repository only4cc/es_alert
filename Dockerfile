FROM python:3.7-alpine
COPY ./src /app
WORKDIR /app
RUN pip install -r requirements.txt

CMD ["python", "date2epoch.py", "2019-03-13T00:00"]
