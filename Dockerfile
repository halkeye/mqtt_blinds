FROM arm32v7/python:3

ENV LANG C.UTF-8

# Install requirements for add-on
RUN apt-get update && apt-get install -y \
    python \
    python-dev \
    python3 \
    mosquitto-clients \
    && rm -rf /var/lib/apt/lists/*
RUN pip install RPi.GPIO

# Copy data for add-on
COPY run.sh blinds.py /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
