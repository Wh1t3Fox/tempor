output "server_ip_address" {
    value = {
        for server in vultr_instance.vps:
        server.label => server.main_ip
    }
}
