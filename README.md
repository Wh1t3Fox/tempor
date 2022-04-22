<h1 align="center">
  <img src="imgs/tempor_med-sm.png" alt="tempor" width="250px" height="250px"></a>
  <br>
</h1>

[![Build Status](https://img.shields.io/travis/com/Wh1t3Fox/tempor?style=for-the-badge)](https://travis-ci.com/Wh1t3Fox/tempor)
[![Coverage](https://img.shields.io/codecov/c/github/wh1t3fox/tempor?style=for-the-badge)](https://codecov.io/gh/Wh1t3Fox/tempor)
[![Python Version](https://img.shields.io/pypi/pyversions/tempor?style=for-the-badge)](https://pypi.org/project/tempor)
[![Pypi Version](https://img.shields.io/pypi/v/tempor?style=for-the-badge)](https://pypi.org/project/tempor)
[![Pypi Downloads](https://img.shields.io/pypi/dm/tempor?style=for-the-badge)](https://pypi.org/project/tempor)
[![Twitter](https://img.shields.io/twitter/follow/_wh1t3fox_?style=for-the-badge)](https://twitter.com/_wh1t3fox_)

**tempor** is a tool used for creating ephemeral infrastructure in the cloud. tempor has the ability to create an arbitrary number of servers via Terraform, ideal for penetration testers and bug hunters.

VPS configuration is performed via Ansible roles after creation. Currently the following roles are executed:
 * [dev-sec.os-hardening](https://github.com/dev-sec/ansible-collection-hardening)
 * [dev-sec.ssh-hardening](https://github.com/dev-sec/ansible-collection-hardening)
 * [geerlingguy.docker](https://github.com/geerlingguy/ansible-role-docker)
 * [geerlingguy.pip](https://github.com/geerlingguy/ansible-role-pip)
   * docker
   * hashcrack-jtr
   * impacket
 * IPv4 and IPv6 iptables lockdown
   * INPUT only allow SSH
   * OUTUT only allow DNS, HTTP/S, DoT
 * More to come...


Currently supported Providers and Images:

| Image | Providers |
| --- | ----------- |
| ArchLinux | Linode, Vultr |
| Centos Stream 9 | DigitalOcean, Linode, Vultr |
| Centos Stream 8 | AWS, DigitalOcean, Linode, Vultr |
| Centos 7 | AWS, DigitalOcean, Linode, Vultr |
| Debian 11 | AWS, DigitalOcean, Linode, Vultr |
| Debian 10 | AWS, DigitalOcean, Linode, Vultr |
| Debian 9 | AWS, DigitalOcean, Linode, Vultr |
| Fedora 35 | DigitalOcean, Linode, Vultr |
| Fedora 34 | DigitalOcean, Linode, Vultr |
| Kali | AWS |
| Ubuntu 21.10 | AWS, DigitalOcean, Linode, Vultr |
| Ubuntu 20.04 | AWS, Azure, DigitalOcean, GCP, Linode, Vultr |
| Ubuntu 18.04 | AWS, DigitalOcean, Linode, Vultr |

  
#### Total Setup Times
```
# bare setup
tempor -p aws -i ubuntu_20-04 -s -b  10.54s user 1.15s system 26% cpu 44.542 total

# minimal  setup
tempor -p aws -i ubuntu_20-04 -s -m  37.36s user 4.22s system 18% cpu 3:42.71 total
  
# full setup
tempor -p aws -i ubuntu_20-04 -s  96.83s user 15.69s system 22% cpu 8:20.32 total

# teardown
tempor -p aws -i ubuntu_20-04 --teardown  8.25s user 1.15s system 23% cpu 39.431 total

```
  
### :moneybag: Referrals - Get Free Credit! :moneybag:

[<img alt="Digital Ocean" src="https://camo.githubusercontent.com/400ad3149c13b05a823e670798697f51ac12f2f5b4a9868dd23dab4f1e21be26/68747470733a2f2f696d616765732e707269736d69632e696f2f7777772d7374617469632f34396161306130392d303664322d346262612d616432302d3462636265353661633530375f6c6f676f2e706e67" height="25px"/>](https://www.digitalocean.com/?refcode=e1c9af803a83)  
[<img alt="Vultr" src="https://www.vultr.com/media/logo_onwhite.svg" height="25px"/>](https://www.vultr.com/?ref=8742641)  
[<img alt="Linode" src="https://www.linode.com/wp-content/uploads/2018/10/linode-logo-blk-rgb-minified.svg" height="31px"/>](https://www.linode.com/?r=94d58b46cdd9ef8ee607abb44a87eb204fa05940)  


###  :heavy_plus_sign: Install :heavy_plus_sign:
```
python3 -m pip install --user tempor
```

#### :wrench: Dependencies :wrench:
- Python >= 3.6
- Windows - [Microsoft Visual C++ 14.0](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

tempor runs on *arm*, *aarch64*, *386*, *amd64*, (Linux, Android), and *Darwin* (MacOS X). tempor requires Windows Subsystem for Linux (WSL) for execution on Windows due to the use of fnctl in ansible_runner.

### :gear: Configuration :gear:
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
  -
    name: aws
    api_token:
      region: REGION
      access_key: ACCESS_KEY
      secret_key: SECRET_KEY
  -
    name: gcp
    api_token:
      auth_file: PATH_TO_JSON_AUTH_FILE
      project: PROJECT_NAME
      region: REGION
      zone: ZONE
  -
    name: azure
    api_token:
      subscription_id: SUBSCRIPTION_ID
      client_id: APP_ID
      client_secret: PASSWORD
      tenant_id: TENANT_ID

default: digitalocean
```

### :interrobang: Usage :interrobang:
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



Inspired by [pry0cc/axiom](https://github.com/pry0cc/axiom).
