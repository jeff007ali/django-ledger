FROM python:3.8

# The enviroment variable ensures that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN mkdir /ledger

WORKDIR /ledger

ADD . /ledger/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt