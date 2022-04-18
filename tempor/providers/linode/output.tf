output "instance_ip_address" {
    value = {
        for instance in linode_instance.vps:
        instance.label => instance.ip_address
    }
}

