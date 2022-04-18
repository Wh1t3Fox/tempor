FROM python:3-bullseye

ENV DEBIAN_FRONTEND=noninteractive
RUN \
  apt-get update -y && \
  apt-get install -y \
    jq \
    wamerican \
    --no-install-recommends && \
  useradd --create-home --shell /bin/bash user

USER user
WORKDIR /home/user/

COPY . /tmp/tempor

ENV PATH="/home/user/.local/bin:${PATH}"
RUN python3 -m pip install --user /tmp/tempor

ENTRYPOINT ["tempor"]
CMD ["--help"]
