FROM python:3.10.9

RUN useradd -u 1000 -ms /bin/bash user

WORKDIR /home/user/app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

ENV PYTHONPATH=/home/user/app

USER user

CMD sleep infinity
