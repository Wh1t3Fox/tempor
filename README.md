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

**tempor** is a tool used for creating ephemeral infrastructure in the cloud. 
tempor has the ability to create an arbitrary number of servers via Terraform, 
ideal for penetration testers and bug hunters.

<p>
AWS supports authentication through ENV variables, profile or API tokens in the config file.
</p>

Custom Ansible playbook supported using ```--ansible``` flag.
  
Custom Packer config supported using ```--packer``` flag.

<p>
Check out the examples/ folder for Ansible and Packer examples
</p>
  
### :moneybag: Referrals - Get Free Credit! :moneybag:

[![DigitalOcean Referral Badge](https://web-platforms.sfo2.digitaloceanspaces.com/WWW/Badge%203.svg)](https://www.digitalocean.com/?refcode=01f2b1191a36&utm_campaign=Referral_Invite&utm_medium=Referral_Program&utm_source=badge)

[<img alt="Vultr" src="https://www.vultr.com/media/logo_onwhite.svg" height="65"/>](https://www.vultr.com/?ref=8742641)  
[<img alt="Linode" src="https://refermehappy.com/static/img/deals/300x150/linode.png" height="65" />](https://www.linode.com/?r=94d58b46cdd9ef8ee607abb44a87eb204fa05940)  


###  :heavy_plus_sign: Install
```
python3 -m pip install --user tempor
```

#### :wrench: Dependencies
- Python >= 3.11
- Windows - WSL only

### :gear: Configuration
```
# ~/.config/tempor/config.yml

providers:
  -
    name: digitalocean
    region: nyc1
    image: ubuntu-20-04-x64
    resources: s-1vcpu-1gb
    api_token:
  -
    name: linode
    region: us-east
    image: linode/ubuntu20.04
    resources: g6-standard-1
    api_token:
  -
    name: vultr
    region: ewr
    image: 387
    resources: vc2-1c-1gb
    api_token:
  -
    name: aws
    region: us-east-1
    image: ami-04505e74c0741db8d
    resources: t2.micro
    api_token:
      profile:    # Optional
      access_key: # Optional
      secret_key: # Optional
  -
    name: gcp
    region: us-east1
    zone: us-east1-b
    image: ubuntu-os-cloud/ubuntu-1804-lts
    resources: f1-micro
    api_token:
      auth_file:
      project:
  -
    name: azure
    region: westus2
    image: Canonical/UbuntuServer/18_04-lts-gen2
    resources: Standard_F2
    api_token:
      subscription_id:
      client_id:
      client_secret:
      tenant_id:
```

### :interrobang: Usage
```
❯ tempor --help
usage: tempor [-h] {digitalocean,linode,vultr,aws,gcp,azure} ...

positional arguments:
  {digitalocean,linode,vultr,aws,gcp,azure}

options:
  -h, --help            show this help message and exit
  -t TEARDOWN, --teardown TEARDOWN
                        Name of VPS Image to Tear down
  -u, --update          Check for Upates
  --version             Print current version

❯ tempor linode --help --additional-info

usage: tempor linode [-h] [--image image] [--region region] [-s] [-l] [-b] [-m] [--teardown]

options:
  -h, --help            show this help message and exit
  -c, --count           Number of images to create
  --image image         Specify the OS Image
  --region region       Specify the Region to Host the Image
  --resources resource  Specify the hardware resources for the host image
  -s, --setup           Create a VPS
  --ansible ansible     Specify Ansible playbook for custom configuration (Path to main.yml file)
  --packer packer       Specify Packer config for custom configuration (Path to *.pkr.hcl file)
  --additional-info     Displays available regions, images, and resources (with --help)

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
                           Images x86-64
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
│ linode/debian11-kube-v1.21.12 │ Kubernetes 1.21.12 on Debian 11 │
│ linode/debian11-kube-v1.21.9  │ Kubernetes 1.21.9 on Debian 11  │
│ linode/debian9-kube-v1.22.2   │ Kubernetes 1.22.2 on Debian 9   │
│ linode/debian11-kube-v1.22.6  │ Kubernetes 1.22.6 on Debian 11  │
│ linode/debian11-kube-v1.22.9  │ Kubernetes 1.22.9 on Debian 11  │
│ linode/debian11-kube-v1.23.4  │ Kubernetes 1.23.4 on Debian 11  │
│ linode/debian11-kube-v1.23.6  │ Kubernetes 1.23.6 on Debian 11  │
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
                         Hardware Resources
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ID               ┃ Price      ┃ Description                      ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ g6-nanode-1      │ $0.0075/hr │ Nanode 1GB                       │
│ g6-standard-1    │ $0.015/hr  │ Linode 2GB                       │
│ g6-standard-2    │ $0.03/hr   │ Linode 4GB                       │
│ g6-standard-4    │ $0.06/hr   │ Linode 8GB                       │
│ g6-standard-6    │ $0.12/hr   │ Linode 16GB                      │
│ g6-standard-8    │ $0.24/hr   │ Linode 32GB                      │
│ g6-standard-16   │ $0.48/hr   │ Linode 64GB                      │
│ g6-standard-20   │ $0.72/hr   │ Linode 96GB                      │
│ g6-standard-24   │ $0.96/hr   │ Linode 128GB                     │
│ g6-standard-32   │ $1.44/hr   │ Linode 192GB                     │
│ g7-highmem-1     │ $0.09/hr   │ Linode 24GB                      │
│ g7-highmem-2     │ $0.18/hr   │ Linode 48GB                      │
│ g7-highmem-4     │ $0.36/hr   │ Linode 90GB                      │
│ g7-highmem-8     │ $0.72/hr   │ Linode 150GB                     │
│ g7-highmem-16    │ $1.44/hr   │ Linode 300GB                     │
│ g6-dedicated-2   │ $0.045/hr  │ Dedicated 4GB                    │
│ g6-dedicated-4   │ $0.09/hr   │ Dedicated 8GB                    │
│ g6-dedicated-8   │ $0.18/hr   │ Dedicated 16GB                   │
│ g6-dedicated-16  │ $0.36/hr   │ Dedicated 32GB                   │
│ g6-dedicated-32  │ $0.72/hr   │ Dedicated 64GB                   │
│ g6-dedicated-48  │ $1.08/hr   │ Dedicated 96GB                   │
│ g6-dedicated-50  │ $1.44/hr   │ Dedicated 128GB                  │
│ g6-dedicated-56  │ $2.88/hr   │ Dedicated 256GB                  │
│ g6-dedicated-64  │ $5.76/hr   │ Dedicated 512GB                  │
│ g1-gpu-rtx6000-1 │ $1.5/hr    │ Dedicated 32GB + RTX6000 GPU x1  │
│ g1-gpu-rtx6000-2 │ $3.0/hr    │ Dedicated 64GB + RTX6000 GPU x2  │
│ g1-gpu-rtx6000-3 │ $4.5/hr    │ Dedicated 96GB + RTX6000 GPU x3  │
│ g1-gpu-rtx6000-4 │ $6.0/hr    │ Dedicated 128GB + RTX6000 GPU x4 │
└──────────────────┴────────────┴──────────────────────────────────┘

❯ tempor linode -b
Generating new key pair...Done.
Preparing Configuration...Done.
Creating VPS...Done.
Configuring SSH Keys...Done.

VPS' now available!

ssh ljtilopnez100

❯ tempor linode --list
                                  Active VPS'
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ VPS Name      ┃ IP Address    ┃ Region  ┃ Image              ┃ Hardware      ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ ljtilopnez100 │ 66.228.46.192 │ us-east │ linode/ubuntu20.04 │ g6-standard-1 │
└───────────────┴───────────────┴─────────┴────────────────────┴───────────────┘

❯ tempor --teardown ljtilopnez100
Tearing down ljtilopnez100...Done.

```



Inspired by [pry0cc/axiom](https://github.com/pry0cc/axiom).

