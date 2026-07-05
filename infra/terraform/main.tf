terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = "project-f537c014-8ae2-4195-9f3"
  region  = "europe-west1"
  zone    = "europe-west1-b"
}

# --- Cloud SQL ---
resource "google_sql_database_instance" "primary" {
  name             = "oasis-db-primary"
  database_version = "POSTGRES_15"
  region           = "europe-west1"
  settings {
    tier = "db-f1-micro"
  }
}

# --- Cloud Run (App-Tier) ---
resource "google_cloud_run_v2_service" "app_tier" {
  name     = "app-tier"
  location = "europe-west1"
  
  template {
    containers {
      image = "europe-west1-docker.pkg.dev/project-f537c014-8ae2-4195-9f3/app-tier-repo/jarvis:latest"
      env {
        name  = "DB_SOCKET_PATH"
        value = "/cloudsql/${google_sql_database_instance.primary.connection_name}"
      }
    }
    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [google_sql_database_instance.primary.connection_name]
      }
    }
  }
}

# --- Qdrant VM (Memory Fabric) ---
resource "google_compute_instance" "qdrant_vm" {
  name         = "qdrant-memory-fabric"
  machine_type = "e2-medium"
  zone         = "europe-west1-b"
  
  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
      size  = 20
    }
  }
  
  network_interface {
    network = "default"
    access_config {}
  }
  
  metadata_startup_script = file("${path.module}/../qdrant-startup.sh")
}
