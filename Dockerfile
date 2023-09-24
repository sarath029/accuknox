FROM python:3.10

LABEL vendor="Social Network"

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1


ENV PYTHONUNBUFFERED 1
WORKDIR /code

RUN apt-get update && apt-get install -y gcc
RUN pip install pipenv && pip install psycopg2

COPY Pipfile Pipfile.lock ./

RUN pipenv install

COPY /entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY /start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start


COPY . ./
EXPOSE 8000

ENTRYPOINT ["/entrypoint"]