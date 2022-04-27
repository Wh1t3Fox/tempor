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

<p>
Supports most images on AWS, Azure, Digital Ocean, GCP, Linode, and Vultr!  
</p>
  
#### Total Setup Times
```
# bare setup
tempor aws -b  10.54s user 1.15s system 26% cpu 44.542 total

# minimal  setup
tempor aws -m  37.36s user 4.22s system 18% cpu 3:42.71 total
  
# full setup
tempor aws -s  96.83s user 15.69s system 22% cpu 8:20.32 total

# teardown
tempor aws --teardown  8.25s user 1.15s system 23% cpu 39.431 total

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
    region: nyc1
    image: ubuntu-20-04-x64
    api_token:
  -
    name: linode
    region: us-east
    image: linode/ubuntu20.04
    api_token:
  -
    name: vultr
    region: ewr
    image: 387
    api_token:
  -
    name: aws
    region: us-east-1
    image: ami-04505e74c0741db8d
    api_token:
      access_key:
      secret_key:
  -
    name: gcp
    region: us-east1
    zone: us-east1b
    image: ubuntu-os-cloud/ubuntu-1804-lts
    api_token:
      auth_file:
      project:
  -
    name: azure
    region: westus2
    image: Canonical/UbuntuServer/18_04-lts-gen2
    api_token:
      subscription_id:
      client_id:
      client_secret:
      tenant_id:

default: digitalocean
```

### :interrobang: Usage :interrobang:
```
❯ tempor --help
usage: tempor [-h] {digitalocean,linode,vultr,aws,gcp,azure} ...

positional arguments:
  {digitalocean,linode,vultr,aws,gcp,azure}

options:
  -h, --help            show this help message and exit

❯ tempor linode --help

usage: tempor linode [-h] [--image image] [--region region] [-s] [-l] [-b] [-m] [--teardown]

options:
  -h, --help       show this help message and exit
  --image image    Specify the OS Image
  --region region  Specify the Region to Host the Image
  -s, --setup      Create VPS'
  -l, --list       List Available VPS'
  -b, --bare       Leave as a Bare Install
  -m, --minimal    Minimal Configuration
  --teardown       Tear down VPS'

          Regions
┏━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ ID           ┃ Location ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ ap-west      │ in       │
│ ca-central   │ ca       │
│ ap-southeast │ au       │
│ us-central   │ us       │
│ us-west      │ us       │
│ us-southeast │ us       │
│ us-east      │ us       │
│ eu-west      │ uk       │
│ ap-south     │ sg       │
│ eu-central   │ de       │
│ ap-northeast │ jp       │
└──────────────┴──────────┘
                              Images
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ID                            ┃ Name                            ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ linode/almalinux8             │ AlmaLinux 8                     │
│ linode/alpine3.12             │ Alpine 3.12                     │
│ linode/alpine3.13             │ Alpine 3.13                     │
│ linode/alpine3.14             │ Alpine 3.14                     │
│ linode/alpine3.15             │ Alpine 3.15                     │
│ linode/arch                   │ Arch Linux                      │
│ linode/centos7                │ CentOS 7                        │
│ linode/centos-stream8         │ CentOS Stream 8                 │
│ linode/centos-stream9         │ CentOS Stream 9                 │
│ linode/debian10               │ Debian 10                       │
│ linode/debian11               │ Debian 11                       │
│ linode/debian9                │ Debian 9                        │
│ linode/fedora34               │ Fedora 34                       │
│ linode/fedora35               │ Fedora 35                       │
│ linode/gentoo                 │ Gentoo                          │
│ linode/debian11-kube-v1.20.15 │ Kubernetes 1.20.15 on Debian 11 │
│ linode/debian9-kube-v1.20.7   │ Kubernetes 1.20.7 on Debian 9   │
│ linode/debian9-kube-v1.21.1   │ Kubernetes 1.21.1 on Debian 9   │
│ linode/debian11-kube-v1.21.9  │ Kubernetes 1.21.9 on Debian 11  │
│ linode/debian9-kube-v1.22.2   │ Kubernetes 1.22.2 on Debian 9   │
│ linode/debian11-kube-v1.22.6  │ Kubernetes 1.22.6 on Debian 11  │
│ linode/debian11-kube-v1.23.4  │ Kubernetes 1.23.4 on Debian 11  │
│ linode/opensuse15.3           │ openSUSE Leap 15.3              │
│ linode/rocky8                 │ Rocky Linux 8                   │
│ linode/slackware14.2          │ Slackware 14.2                  │
│ linode/slackware15.0          │ Slackware 15.0                  │
│ linode/ubuntu16.04lts         │ Ubuntu 16.04 LTS                │
│ linode/ubuntu18.04            │ Ubuntu 18.04 LTS                │
│ linode/ubuntu20.04            │ Ubuntu 20.04 LTS                │
│ linode/ubuntu21.10            │ Ubuntu 21.10                    │
│ linode/ubuntu22.04            │ Ubuntu 22.04 LTS                │
│ linode/alpine3.11             │ Alpine 3.11                     │
│ linode/centos8                │ CentOS 8                        │
│ linode/fedora33               │ Fedora 33                       │
│ linode/opensuse15.2           │ openSUSE Leap 15.2              │
│ linode/slackware14.1          │ Slackware 14.1                  │
│ linode/ubuntu21.04            │ Ubuntu 21.04                    │
└───────────────────────────────┴─────────────────────────────────┘

➜ tempor linode --setup
Preparing Configuration...Done.
Creating VPS...Done.
Configuring SSH Keys...Done.

VPS' now available!

ssh nnvnv620

➜ tempor linode --list
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
