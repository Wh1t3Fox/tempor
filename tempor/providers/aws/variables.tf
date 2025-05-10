variable "api_token" {}

variable "num" {
	default = 1
}

variable "username" {
  default = "user"
}

variable "image" {
  default = "ami-0f9fc25dd2506cf6d"
}

variable "region" {
  default = "us-east-1"
}

variable "resources" {
  default = "t2.micro"
}

variable "tags" {
  default = {}
}

variable "vpc_name" {
  default = "tempor-vpc"
}

variable "igw_name" {
  default = "tempor-IGW"
}

variable "rt_name" {
  default = "tempor-route-table"
}

variable "subnet_name" {
  default = "tempor-subnett"
}

variable "vps_name" {
  default = ""
}

variable "cidr_block" {
  default = "10.253.0.0/16"
}
