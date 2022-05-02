variable "api_token" {}
variable "num" {
	default = 1
}
variable "username" {
	default = "user"
}
variable "image" {
    default = "linode/ubuntu20.04"
}
variable "region" {
    default = "us-east"
}
variable "resources" {
    default = "g6-standard-1"
}
