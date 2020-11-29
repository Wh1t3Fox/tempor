data "external" "vps_name" {
  program = ["python3", "${path.module}/external/name-generator.py"]
}

data "external" "root_pass" {
  program = ["python3", "${path.module}/external/passwd-generator.py"]
}
