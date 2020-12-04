# tempor

[![Build Status](https://img.shields.io/travis/com/Wh1t3Fox/tempor?style=for-the-badge)](https://travis-ci.com/Wh1t3Fox/tempor)
[![Python Version](https://img.shields.io/pypi/pyversions/tempor?style=for-the-badge)](https://pypi.org/project/tempor)
[![Pypi Version](https://img.shields.io/pypi/v/tempor?style=for-the-badge)](https://pypi.org/project/tempor)
[![Pypi Downloads](https://img.shields.io/pypi/dm/tempor?style=for-the-badge)](https://pypi.org/project/tempor)



Inspired by [pry0cc/axiom](https://github.com/pry0cc/axiom). Currently supports creating machines on Digital Ocean, Linode, and Vultr.

### Install
```
python3 -m pip install --user tempor
```

### Configuration
```
# ~/.config/tempor/config.yml

providers:
  -
    name: digitalocean
    api_token: API_TOKEN_HERE
  -
    name: linode
    api_token: API_TOKEN_HERE
  -
    name: vultr
    api_token: API_TOKEN_HERE

default: digitalocean
```

### Usage
```
➜ tempor -h
usage: tempor [-h] [-p PROVIDER] [-c COUNT] [--setup] [--list]
              [--no-config] [--teardown]

optional arguments:
  -h, --help            show this help message and exit
  -p PROVIDER, --provider PROVIDER
                        Specify the Provider Name
  -c COUNT, --count COUNT
                        Number of Images to Create
  --setup               Setup Image(s)
  --list                List Available Images
  --no-config           Leave as a Bare Install
  --teardown            Tear down VPS

➜ tempor --setup
Preparing Configuration...Done.
Creating VPS...Done.
Configuring SSH Keys...Done.

VPS' now available!

ssh nnvnv620

➜ tempor --list
         Active VPS'
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ VPS Name ┃ IP Address     ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ nnvnv620 │ 178.128.144.45 │
└──────────┴────────────────┘

➜ tempor --teardown
Tearing down...Done.

```
