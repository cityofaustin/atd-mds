#
# ATD MDS Data Publisher
# An ETL data processor that uses Python 3.8 that publishes
# data to a PostgreSQL database via GraphQL and Socrata
#

#FROM python:3.8-alpine3.10
FROM python:3.8.1-slim-buster

WORKDIR /app

COPY . /app

RUN apt-get update && \
    apt-get install libspatialindex-dev -y && \
    pip install -r requirements_production.txt

EXPOSE 5555/tcp

CMD ["sh"]
