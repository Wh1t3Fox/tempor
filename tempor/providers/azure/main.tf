provider "azurerm" {
    features {}
    environment = "public"
    subscription_id = var.api_token.subscription_id
    client_id = var.api_token.client_id
    client_secret = var.api_token.client_secret
    tenant_id = var.api_token.tenant_id
}

resource "azurerm_resource_group" "main" {
    name = "${var.vps_name == "" ? data.external.vps_name.result.name : var.vps_name}-resource"
    location = var.region
}

resource "azurerm_virtual_network" "main" {
  name                = "${var.vps_name == "" ? data.external.vps_name.result.name : var.vps_name}-network"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_subnet" "internal" {
  name                 = "internal"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.2.0/24"]
}

resource "azurerm_public_ip" "public_ip" {
  name                = "${var.vps_name == "" ? data.external.vps_name.result.name : var.vps_name}-public_ip"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  allocation_method   = "Dynamic"
}

resource "azurerm_network_interface" "main" {
  name                = "${var.vps_name == "" ? data.external.vps_name.result.name : var.vps_name}-nic1"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  ip_configuration {
    name                          = "primary"
    subnet_id                     = azurerm_subnet.internal.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.public_ip.id
  }
}

resource "azurerm_network_interface" "internal" {
  name                = "${var.vps_name == "" ? data.external.vps_name.result.name : var.vps_name}-nic2"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.internal.id
    private_ip_address_allocation = "Dynamic"
  }
}

resource "azurerm_network_security_group" "ssh" {
    name = "${var.vps_name == "" ? data.external.vps_name.result.name : var.vps_name}-fw"
    location            = azurerm_resource_group.main.location
    resource_group_name = azurerm_resource_group.main.name
    security_rule {
        name                       = "AllowSSH"
        description                = "Allow SSH"
        priority                   = 150
        direction                  = "Inbound"
        access                     = "Allow"
        protocol                   = "Tcp"
        source_port_range          = "*"
        destination_port_range     = "22"
        source_address_prefix      = "Internet"
        destination_address_prefix = "*"
    }
}

resource "azurerm_network_interface_security_group_association" "main" {
  network_interface_id      = azurerm_network_interface.internal.id
  network_security_group_id = azurerm_network_security_group.ssh.id
}

resource "azurerm_linux_virtual_machine" "vps" {
    count = var.num
    name = "${var.vps_name == "" ? data.external.vps_name.result.name : var.vps_name}${var.num == 1 ? "" : count.index}"
    resource_group_name = azurerm_resource_group.main.name
    location = azurerm_resource_group.main.location
    size = var.resources
    admin_username = "root"
    network_interface_ids = [
        azurerm_network_interface.main.id,
        azurerm_network_interface.internal.id,
    ]

    admin_ssh_key {
        username = "root"
        public_key = file("${path.module}/files/${var.region}/${var.image}/${var.vps_name == "" ? data.external.vps_name.result.name : var.vps_name}/.ssh/id_rsa.pub")
    }

    os_disk {
        caching = "ReadWrite"
        storage_account_type = "Standard_LRS"
    }

    source_image_reference {
        publisher = element(split("/", var.image), 0)
        offer = element(split("/", var.image), 1)
        sku = element(split("/", var.image), 2)
        version = "latest"
    }
}


