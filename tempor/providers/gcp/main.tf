provider "google" {
  credentials = file(var.api_token.auth_file)
  project     = var.api_token.project
  region      = var.region
}

# allow ssh
resource "google_compute_firewall" "allow-ssh" {
    name = "${data.external.vps_name.result.name}-fw-ssh"
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
    name = "${data.external.vps_name.result.name}${count.index}"
    machine_type = "f1-micro"
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
        ssh-keys = "root:${file("${path.module}/files/.ssh/id_ed25519.pub")}"
    }
}


