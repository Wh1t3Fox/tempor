variable "api_token" {}
variable "num" {
	default = 1
}
variable "username" {
    default = "user"
}
variable "image" {
    default = "ami-04505e74c0741db8d"
}
variable "region" {
    default = "us-east-1"
}
variable "resources" {
    default = "t2.micro"
}
