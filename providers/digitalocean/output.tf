output "droplet_ip_address" {
    value = {
        for droplet in digitalocean_droplet.vps:
        droplet.name => droplet.ipv4_address
    }
}

