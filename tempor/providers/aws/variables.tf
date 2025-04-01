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
variable "vps_name" {
  default = ""
}
