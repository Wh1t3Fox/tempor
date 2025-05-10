
resource "aws_vpc" "tempor" {
  cidr_block = var.cidr_block
  assign_generated_ipv6_cidr_block = true

  tags = {
   Name = var.vpc_name
  }
}
