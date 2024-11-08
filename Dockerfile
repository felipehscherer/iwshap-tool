FROM ubuntu:24.04
RUN apt-get update && \
    apt-get upgrade -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    wget vim python3-pip python3-dev build-essential python3-venv sudo
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"
WORKDIR /IWSHAP
COPY . ./
RUN pip3 install -r requirements.txt