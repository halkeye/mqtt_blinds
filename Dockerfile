ARG BUILD_FROM=arm32v7/python:3
FROM $BUILD_FROM

ENV LANG C.UTF-8

# Install requirements for add-on
RUN apk --no-cache add python3 jq mosquitto-clients
RUN apk add --update \
    python \
    python-dev \
    py-pip \
    build-base \
    && pip install virtualenv \
    && rm -rf /var/cache/apk/*
RUN pip install RPi.GPIO

# Copy data for add-on
COPY run.sh blinds.py /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
