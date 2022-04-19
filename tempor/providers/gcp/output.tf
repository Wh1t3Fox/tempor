output "instance_ip_address" {
    value = {
        for instance in google_compute_instance.vps:
        instance.name => instance.network_interface.0.access_config.0.nat_ip
    }
}

