FROM python:3.8-slim

RUN apt-get update && \
apt-get install -y --no-install-recommends \
        --fix-missing \
        openjdk-11-jre-headless


ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64


ENV PYTHONUNBUFFERED 1
ENV DISPLAY=:99

# Install apt dependencies
RUN apt update && apt upgrade

RUN apt install tar

# Install requirements
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . /app

ARG SPARK_ARCHIVE=https://archive.apache.org/dist/spark/spark-3.1.2/spark-3.1.2-bin-hadoop3.2.tgz
ENV SPARK_HOME /app/spark-3.1.2-bin-hadoop3.2

ENV PATH $PATH:${SPARK_HOME}/bin

WORKDIR /app

ADD $SPARK_ARCHIVE .
RUN tar -xzf spark-3.1.2-bin-hadoop3.2.tgz
ENTRYPOINT python model_driver.py