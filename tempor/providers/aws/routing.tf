
resource "aws_internet_gateway" "tempor_igw" {
  vpc_id = aws_vpc.tempor.id

  tags = {
    "Name" = var.igw_name
  }
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.tempor.id

    route {
      cidr_block = "0.0.0.0/0"
      gateway_id = aws_internet_gateway.tempor_igw.id
    }

    route {
      ipv6_cidr_block = "::/0"
      gateway_id = aws_internet_gateway.tempor_igw.id
  }


  tags = {
    "Name" = var.rt_name
  }
}

resource "aws_subnet" "tempor_subnet" {
  vpc_id = aws_vpc.tempor.id

  ipv6_cidr_block = cidrsubnet(aws_vpc.tempor.ipv6_cidr_block, 8, 0)
  cidr_block = cidrsubnet(aws_vpc.tempor.cidr_block, 8, 0)
  availability_zone_id = data.aws_availability_zones.available.zone_ids[0]

  assign_ipv6_address_on_creation = true
  map_public_ip_on_launch = true


  tags = {
    Name = var.subnet_name
  }
}

resource "aws_route_table_association" "public-rt-sb-association" {
  subnet_id      = aws_subnet.tempor_subnet.id
  route_table_id = aws_route_table.public_rt.id
}

