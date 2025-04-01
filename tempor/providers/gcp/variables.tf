variable "api_token" {}
variable "num" {
	default = 1
}
variable "username" {
	default = "user"
}
variable "image" {
    default = "ubuntu-os-cloud/ubuntu-2004-lts"
}
variable "region" {
    default = "us-east1"
}
variable "zone" {
    default = "us-east1-b"
}
variable "resources" {
    default = "f1-micro"
}
variable "vps_name" {
  default = ""
}
