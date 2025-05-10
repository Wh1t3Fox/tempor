provider "aws" {}

resource "aws_key_pair" "default" {
    key_name = "${var.vps_name == "" ? data.external.vps_name.result.name : var.vps_name}"
    public_key = chomp(file("${path.module}/files/${var.region}/${var.image}/${var.vps_name == "" ? data.external.vps_name.result.name : var.vps_name}/.ssh/id_ed25519.pub"))
}

resource "aws_instance" "vps" {
  count = var.num
  ami = var.image
  instance_type = var.resources
  associate_public_ip_address = "true"
  key_name = aws_key_pair.default.key_name

  subnet_id = aws_subnet.tempor_subnet.id

  vpc_security_group_ids = [
    aws_security_group.allow_ssh.id
  ]

  tags = merge({
    Name = "${var.vps_name == "" ? data.external.vps_name.result.name : var.vps_name}${var.num == 1 ? "" : count.index}"
  }, var.tags)
}


