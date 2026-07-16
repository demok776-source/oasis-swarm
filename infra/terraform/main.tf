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

  # Prevents `terraform destroy` / an errant `apply` from ever silently
  # dropping the primary database. This was unset before -- the provider
  # default leaves the instance fully destroyable with no confirmation
  # beyond the usual `-auto-approve` flag already used in deploy.yml.
  deletion_protection = true

  settings {
    tier = "db-f1-micro"

    # No backups/PITR were configured at all -- a single bad migration or
    # `DROP TABLE` would have been unrecoverable. Daily backups + 7 days of
    # write-ahead-log retention for point-in-time recovery.
    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 7
      }
    }

    ip_configuration {
      # require_ssl is deprecated in favor of ssl_mode as of provider 5.x,
      # but both are set here for compatibility across provider minor
      # versions; ssl_mode takes precedence where both are recognized.
      require_ssl = true
      ssl_mode    = "ENCRYPTED_ONLY"
    }
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

# --- Redis VM (Sync Layer event bus) ---
# Documented in infra/README.md's architecture diagram and cost table
# ("Redis VM | e2-micro | ~$6") but never actually defined here before --
# app-tier's Sync Layer had no durable Redis to talk to in the Terraform-
# managed environment at all.
resource "google_compute_instance" "redis_vm" {
  name         = "redis-sync-layer"
  machine_type = "e2-micro"
  zone         = "europe-west1-b"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
      size  = 10
    }
  }

  network_interface {
    network = "default"
    access_config {}
  }

  metadata_startup_script = file("${path.module}/../redis-startup.sh")
}

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
