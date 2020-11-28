FROM python:3-stretch

ENV DEBIAN_FRONTEND=noninteractive
RUN \
  apt-get update -y && \
  apt-get install -y \
    jq \
    wamerican \
    unzip \
    --no-install-recommends && \
  python -m pip install -U pip && \
  python -m pip install -U \
    python-terraform && \
  TER_VER=`curl -s https://api.github.com/repos/hashicorp/terraform/releases/latest | grep tag_name | cut -d: -f2 | tr -d \"\,\v | awk '{$1=$1};1'` && \
  wget https://releases.hashicorp.com/terraform/${TER_VER}/terraform_${TER_VER}_linux_amd64.zip && \
  unzip terraform_${TER_VER}_linux_amd64.zip && \
  rm terraform_${TER_VER}_linux_amd64.zip && \
  mv terraform /usr/local/bin/

WORKDIR /work
