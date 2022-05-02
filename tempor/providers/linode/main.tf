provider "linode" {
  token = var.api_token
}

resource "linode_sshkey" "default" {
    label = data.external.vps_name.result.name
    ssh_key = chomp(file("${path.module}/files/${var.region}/${var.image}/.ssh/id_ed25519.pub"))
}

#resource "linode_stackscript" "script" {
#    label = "script"
#    description = "Install new User"
#    script = <<-EOF
##!/bin/bash
## <UDF name="username" label="Username" example="nginx" default="">
## <UDF name="sshkey" label="SSH Pub Key" example="nginx" default="">
#
#sudo useradd -m -s /bin/bash -G sudo $USERNAME
#sudo mkdir -p /home/$USERNAME/.ssh
#sudo touch /home/$USERNAME/.ssh/authorized_keys
#sudo echo $SSHKEY > /home/$USERNAME/.ssh/authorized_keys
#sudo chown $USERNAME:$USERNAME -R /home/$USERNAME
#sudo chmod 700 /home/$USERNAME/.ssh
#sudo chmod 600 /home/$USERNAME/.ssh/authorized_keys
#sudo usermod -aG sudo $USERNAME
#sudo echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/90-custom-init-users
#EOF
#
#    images = [
#        "linode/centos7",
#        "linode/centos-stream8",
#        "linode/centos-stream9",
#        "linode/debian10",
#        "linode/debian11",
#        "linode/debian9",
#        "linode/fedora34",
#        "linode/fedora35",
#        "linode/ubuntu16.04lts",
#        "linode/ubuntu18.04",
#        "linode/ubuntu20.04",
#        "linode/ubuntu21.10",
#        "linode/ubuntu22.04",
#        "linode/alpine3.11",
#        "linode/centos8",
#        "linode/fedora33",
#        "linode/ubuntu21.04"
#    ]
#}

resource "linode_instance" "vps" {
    count = var.num
    image = var.image
    label = "${data.external.vps_name.result.name}${count.index}"
    region = var.region
    type = var.resources
    root_pass = data.external.root_pass.result.value
    authorized_keys = [linode_sshkey.default.ssh_key]

    #stackscript_id = linode_stackscript.script.id
    #stackscript_data = {
    #    username = var.username
    #    sshkey = linode_sshkey.default.ssh_key
    #}
}


