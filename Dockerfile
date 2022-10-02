FROM python:latest as base

WORKDIR /app

RUN apt-get update
RUN apt-get install -y \
    build-essential \
    curl \
    ffmpeg
RUN apt-get update
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y
RUN echo 'source $HOME/.cargo/env' >> $HOME/.bashrc

FROM base as cli
COPY cli-requirements.txt cli-requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/cli-requirements.txt
ENTRYPOINT [ "whisper" ]

FROM base as app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY app.py app.py
ENTRYPOINT [ "python", "app.py" ]
