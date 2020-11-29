output "server_ip_address" {
    value = {
        for server in vultr_server.vps:
        server.name => server.main_ip
    }
}
