# tempor

## Work In Progress...

Inspired by [pry0cc/axiom](https://github.com/pry0cc/axiom). Currently supports creating bare machines on Digital Ocean, Linode, and Vultr.

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
➜ tempor --help
usage: tempor [-h] [-p PROVIDER] [--teardown]

optional arguments:
  -h, --help            show this help message and exit
  -p PROVIDER, --provider PROVIDER
                        Specify the Provider Name
  --teardown            Tear down VPS

```

### TODO:

- [x] Terraform for Machine Creation
- [ ] Machine Setup via Ansible Playbooks
- [ ] Custom Wrapper for Trivial Interaction
- [ ] TBD
