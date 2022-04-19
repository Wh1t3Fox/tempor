provider "aws" {
  access_key = var.api_token.access_key
  secret_key = var.api_token.secret_key
  region = var.api_token.region
}

resource "aws_key_pair" "default" {
    key_name = data.external.vps_name.result.name
    public_key = chomp(file("${path.module}/files/.ssh/id_ed25519.pub"))
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
    ami = "ami-04505e74c0741db8d"
    instance_type = "t2.micro"
    associate_public_ip_address = "true"
    key_name = aws_key_pair.default.key_name

    security_groups = [
        aws_security_group.allow_ssh.name
    ]

    tags = {
        Name = "${data.external.vps_name.result.name}${count.index}"
    }
}


