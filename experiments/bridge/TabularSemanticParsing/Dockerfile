FROM pytorch/pytorch:1.7.0-cuda11.0-cudnn8-devel


# Fix problem with gpg key for next command
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/3bf863cc.pub

RUN apt update && \
    apt install curl -y && \
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.8 get-pip.py

RUN useradd -m user

WORKDIR /home/user/app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

RUN python -m nltk.downloader punkt

COPY . .

ENV PYTHONPATH=/home/user/app

USER user

CMD sleep infinity
