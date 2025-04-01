provider "google" {
  credentials = file(var.api_token.auth_file)
  project     = var.api_token.project
  region      = var.region
}

# allow ssh
resource "google_compute_firewall" "allow-ssh" {
    name = "${var.vps_name == "" ? data.external.vps_name.result.name : var.vps_name}-fw-ssh"
    network = "default"
    allow {
        protocol = "tcp"
        ports    = ["22"]
    }  

    source_ranges = ["0.0.0.0/0"]
    target_tags = ["ssh"]
}


resource "google_compute_instance" "vps" {
    count = var.num
    name = "${var.vps_name == "" ? data.external.vps_name.result.name : var.vps_name}${var.num == 1 ? "" : count.index}"
    machine_type = var.resources
    zone = var.zone
    tags = ["ssh"]

    boot_disk {
        initialize_params {
            image = var.image
        }
    }

    network_interface {
        network = "default"
        access_config {}
    }

    metadata = {
        ssh-keys = "root:${file("${path.module}/files/${var.region}/${var.image}/${var.vps_name == "" ? data.external.vps_name.result.name : var.vps_name}/.ssh/id_ed25519.pub")}"
    }
}


