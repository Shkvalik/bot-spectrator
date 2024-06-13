FROM python:3.11-slim

WORKDIR /usr/src/app/my_project

COPY requirements.txt /usr/src/app/my_project
RUN pip install -r /usr/src/app/my_project/requirements.txt
COPY . /usr/src/app/my_project
