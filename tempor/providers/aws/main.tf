provider "aws" {}

resource "aws_key_pair" "default" {
    key_name = "${var.vps_name == "" ? data.external.vps_name.result.name : var.vps_name}"
    public_key = chomp(file("${path.module}/files/${var.region}/${var.image}/${var.vps_name == "" ? data.external.vps_name.result.name : var.vps_name}/.ssh/id_ed25519.pub"))
}

resource "aws_security_group" "allow_ssh" {
    name = "${var.vps_name == "" ? data.external.vps_name.result.name : var.vps_name}"

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
        Name = "${var.vps_name == "" ? data.external.vps_name.result.name : var.vps_name}"
    }
}

resource "aws_instance" "vps" {
    count = var.num
    ami = var.image
    instance_type = var.resources
    associate_public_ip_address = "true"
    key_name = aws_key_pair.default.key_name

    security_groups = [
        aws_security_group.allow_ssh.name
    ]

    tags = merge({
      Name = "${var.vps_name == "" ? data.external.vps_name.result.name : var.vps_name}${var.num == 1 ? "" : count.index}"
    }, var.tags)
}


