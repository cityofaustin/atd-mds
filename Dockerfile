#
# Docker Base image for Python 3.8 with Rtree and Shapely
#

FROM atddocker/atd-mds-etl-base:latest
# Copy our own application
WORKDIR /app
COPY . /app
# Proceed to install the requirements...do
RUN pip install -r requirements_production.txt
