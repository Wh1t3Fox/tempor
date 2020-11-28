provider "vultr" {
  api_key = var.api_token
  rate_limit = 700
  retry_limit = 3
}

resource "vultr_ssh_key" "default" {
    name = data.external.vps_name.result.name
    ssh_key = chomp(file("${path.module}/files/.ssh/id_ed25519.pub"))
}

resource "vultr_server" "vps" {
    count = 1
    plan_id = "201"
    region_id = "6"
    os_id = "167"
    label = data.external.vps_name.result.name
    ssh_key_ids = [vultr_ssh_key.default.id]
}


