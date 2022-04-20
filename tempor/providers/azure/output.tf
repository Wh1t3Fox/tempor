output "instance_ip_address" {
    value = {
        for instance in azurerm_linux_virtual_machine.vps:
        instance.name => instance.public_ip_address
    }
}

