FROM python:3.7-alpine
COPY ./src /src
WORKDIR /src
RUN pip install -r requirements.txt
RUN apk add --no-cache curl

CMD ["python", "date2epoch.py", "2019-03-13T00:00"]
