FROM nvidia/cuda:11.2.2-devel-ubuntu20.04

# install required linux packages
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt install -y git wget graphviz graphviz-dev

# install conda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /miniconda.sh && bash /miniconda.sh -b -p /opt/conda

ENV PATH="/opt/conda/bin:$PATH"

WORKDIR /app

RUN conda create -n resdsql python=3.8.5

SHELL ["conda", "run", "-n", "resdsql", "/bin/bash", "-c"]

RUN conda install pytorch==1.11.0 torchvision==0.12.0 torchaudio==0.11.0 cudatoolkit=11.3 -c pytorch

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

RUN pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.2.0/en_core_web_sm-2.2.0.tar.gz

COPY resdsql/nltk_downloader.py resdsql/nltk_downloader.py

RUN python resdsql/nltk_downloader.py

WORKDIR /app/resdsql/third_party

RUN git clone https://github.com/ElementAI/spider.git

RUN git clone https://github.com/ElementAI/test-suite-sql-eval.git

RUN mv ./test-suite-sql-eval ./test_suite

WORKDIR /app

COPY . .

SHELL ["/bin/bash", "-c"]

# create non-root user to avoid problem with permissions on host system
RUN useradd -u 1000 -ms /bin/bash user

RUN apt-get update && apt-get install -y sudo

RUN adduser user sudo

# set password of user to "password"
RUN echo "user:password" | chpasswd

USER user

# activate environment by default
RUN conda init

RUN echo "conda activate resdsql" >> ~/.bashrc

CMD conda run -n resdsql streamlit run --server.port 80 app.py --server.enableXsrfProtection=false
