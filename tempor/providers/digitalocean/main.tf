provider "digitalocean" {
  token = var.api_token
}

resource "digitalocean_ssh_key" "default" {
    name = data.external.vps_name.result.name
    public_key = file("${path.module}/files/.ssh/id_ed25519.pub")
}

resource "digitalocean_droplet" "vps" {
    count = var.num
    image = "ubuntu-20-04-x64"
    name = "${data.external.vps_name.result.name}${count.index}"
    region = "nyc1"
    size = "s-1vcpu-1gb"
    ssh_keys = [
        digitalocean_ssh_key.default.fingerprint
    ]

}
