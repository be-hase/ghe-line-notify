FROM python:3.5

MAINTAINER Ryosuke Hasebe <hsb.1014@gmail.com>

ADD . /ghe-line-notify
WORKDIR /ghe-line-notify

RUN pip install -r requirements/common.txt
RUN python manage.py db upgrade

CMD gunicorn app:app -b 0.0.0.0:8000

EXPOSE 8000

