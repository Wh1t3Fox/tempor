provider "linode" {
  token = var.api_token
}

resource "linode_sshkey" "default" {
    label = data.external.vps_name.result.name
    ssh_key = chomp(file("${path.module}/files/.ssh/id_ed25519.pub"))
}

resource "linode_instance" "vps" {
    count = 1
    image = "linode/ubuntu18.04"
    label = data.external.vps_name.result.name
    region = "us-east"
    type = "g6-standard-1"
    root_pass = data.external.root_pass.result.value
    authorized_keys = [linode_sshkey.default.ssh_key]
}


