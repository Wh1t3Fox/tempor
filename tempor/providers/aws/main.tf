provider "aws" {
  access_key = var.api_token.access_key
  secret_key = var.api_token.secret_key
  region = var.region
}

resource "aws_key_pair" "default" {
    key_name = data.external.vps_name.result.name
    public_key = chomp(file("${path.module}/files/${var.region}/${var.image}/.ssh/id_ed25519.pub"))
}

resource "aws_security_group" "allow_ssh" {
    name = "${data.external.vps_name.result.name}"

    ingress {
      description      = "Allow SSH"
      from_port        = 22
      to_port          = 22
      protocol         = "tcp"
      cidr_blocks      = ["0.0.0.0/0"]
      ipv6_cidr_blocks = ["::/0"]
    }

    egress {
      from_port        = 0
      to_port          = 0
      protocol         = "-1"
      cidr_blocks      = ["0.0.0.0/0"]
      ipv6_cidr_blocks = ["::/0"]
    }

    tags = {
        Name = "${data.external.vps_name.result.name}"
    }
}

resource "aws_instance" "vps" {
    count = var.num
    ami = var.image
    instance_type = var.resources
    associate_public_ip_address = "true"
    key_name = aws_key_pair.default.key_name

    user_data = <<-EOF
#!/bin/bash
sudo useradd -m -s /bin/bash -G sudo ${var.username}
sudo mkdir -p /home/${var.username}/.ssh
sudo touch /home/${var.username}/.ssh/authorized_keys
sudo echo ${aws_key_pair.default.public_key} > /home/${var.username}/.ssh/authorized_keys
sudo chown ${var.username}:${var.username} -R /home/${var.username}
sudo chmod 700 /home/${var.username}/.ssh
sudo chmod 600 /home/${var.username}/.ssh/authorized_keys
sudo usermod -aG sudo ${var.username}
sudo echo "${var.username} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/90-custom-init-users
EOF

    security_groups = [
        aws_security_group.allow_ssh.name
    ]

    tags = {
        Name = "${data.external.vps_name.result.name}${count.index}"
    }
}


