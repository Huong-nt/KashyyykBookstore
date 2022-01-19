
# Python support can be specified down to the minor or micro version
# (e.g. 3.6 or 3.6.3).
# OS Support also exists for jessie & stretch (slim and full).
# See https://hub.docker.com/r/library/python/ for all supported Python
# tags from Docker Hub.
FROM python:3.7-alpine


# Installing packages
RUN apk update
RUN pip install --no-cache-dir pipenv

# Install API dependencies
RUN apk add --no-cache mariadb-connector-c-dev ;\
    apk add --no-cache --virtual .build-deps build-base mariadb-dev;\
    apk add --no-cache openssl-dev
RUN apk del .build-deps 

# Defining working directory and adding source code
WORKDIR /usr/src/app
COPY Pipfile Pipfile.lock bootstrap.sh ./
RUN pipenv install
COPY code ./code

LABEL Name=bookstore-api Version=2022.01.19
EXPOSE 5002

ENTRYPOINT ["/usr/src/app/bootstrap.sh"]



