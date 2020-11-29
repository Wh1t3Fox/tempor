output "instance_ip_address" {
    value = {
        for instance in linode_instance.vps:
        instance.name => instance.ip_address
    }
}

