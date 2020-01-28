#
# ATD MDS Data Publisher
# An ETL data processor that uses Python 3.8 that publishes
# data to a PostgreSQL database via GraphQL and Socrata
#

FROM python:3.8-alpine3.10

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

EXPOSE 5555/tcp

CMD ["sh"]
