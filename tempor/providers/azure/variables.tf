variable "api_token" {}
variable "num" {
	default = 1
}
variable "username" {
	default = "user"
}
variable "image" {
    default = "Canonical/UbuntuServer/18_04-lts-gen2"
}
variable "region" {
	default = "eastus"
}
variable "resources" {
	default = "Standard_F2"
}
variable "vps_name" {
  default = ""
}
