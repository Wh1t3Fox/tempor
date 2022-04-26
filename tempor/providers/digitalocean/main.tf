provider "digitalocean" {
  token = var.api_token
}

resource "digitalocean_ssh_key" "default" {
    name = data.external.vps_name.result.name
    public_key = file("${path.module}/files/.ssh/id_ed25519.pub")
}

#data "template_file" "script" {
#    template = file("${path.module}/files/cloud-init.yml")
#    vars = {
#        username = var.username,
#        public_key = digitalocean_ssh_key.default.public_key
#    }
#}

resource "digitalocean_droplet" "vps" {
    count = var.num
    image = var.image
    name = "${data.external.vps_name.result.name}${count.index}"
    region = var.region
    size = "s-1vcpu-1gb"
    ssh_keys = [
        digitalocean_ssh_key.default.fingerprint
    ]
    # user_data = data.template_file.script.rendered
}
