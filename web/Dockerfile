FROM python:3.6.2
LABEL maintainer kohashi
ENV PYTHONUNBUFFERED 1
RUN mkdir /docker_api

WORKDIR /docker_api
COPY requirements.txt /docker_api
RUN pip install -r requirements.txt
# RUN pip install  -i  https://pypi.python.org/simple/  -r requirements.txt