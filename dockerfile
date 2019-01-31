FROM ubuntu:latest

RUN apt-get -y update && apt-get install -y apt-utils apache2 apache2-utils libapache2-mod-wsgi-py3 python3 python3-dev python3-pip libmysqlclient-dev

RUN ln /usr/bin/python3 /usr/bin/python
RUN ln /usr/bin/pip3 /usr/bin/pip

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

COPY requirements.pip requirements.pip
RUN pip install -r requirements.pip

COPY config /bot/config
COPY logs /bot/logs
COPY modules /bot/modules
COPY webhooks.py /bot/webhooks.py

WORKDIR /bot

ENV MY_LOG_DIR=/bot/logs/
ENV MY_CONF_DIR=/bot/config

ENV FLASK_APP=webhooks.py

EXPOSE 5000
CMD [ "python", "-m", "flask", "run", "--host=0.0.0.0" ]