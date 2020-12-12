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
Currently supporting Digital Ocean, Linode, and Vultr. More to come!
</>
  
#### Total Setup Time
```
tempor --setup  39.49s user 8.29s system 16% cpu 4:58.62 total
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
