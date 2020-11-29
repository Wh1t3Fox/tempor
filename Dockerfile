FROM python:3-stretch

ENV DEBIAN_FRONTEND=noninteractive
RUN \
  apt-get update -y && \
  apt-get install -y \
    jq \
    wamerican \
    --no-install-recommends && \
  useradd -m -s /bin/bash user

USER user
WORKDIR /home/user/

COPY . /tmp/tempor

RUN python -m pip install --user /tmp/tempor

ENV PATH=$PATH:/home/user/.local/bin/
ENTRYPOINT ["tempor"]
CMD ["--help"]
