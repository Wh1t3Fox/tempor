output "instance_ip_address" {
    value = {
        for instance in aws_instance.vps:
        instance.tags_all.Name => instance.public_ip
    }
}
