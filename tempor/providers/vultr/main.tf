provider "vultr" {
  api_key = var.api_token
  rate_limit = 700
  retry_limit = 3
}

resource "vultr_ssh_key" "default" {
    name = data.external.vps_name.result.name
    ssh_key = chomp(file("${path.module}/files/${var.region}/${var.image}/.ssh/id_ed25519.pub"))
}

resource "vultr_instance" "vps" {
    count = var.num
    os_id = var.image
    plan = var.resources
    region = var.region
    label = "${data.external.vps_name.result.name}${count.index}"
    ssh_key_ids = [vultr_ssh_key.default.id]
}


