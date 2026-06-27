# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ==============================================================================
# Variables
# ==============================================================================

variable "gemini_api_key" {
  type        = string
  description = "Gemini API Key"
  default     = ""
}

variable "user_api_key" {
  type        = string
  description = "Caregiver User API Key"
  default     = ""
}

variable "admin_api_key" {
  type        = string
  description = "Admin API Key"
  default     = ""
}

# ==============================================================================
# Managed Database (Google Cloud SQL PostgreSQL)
# ==============================================================================

resource "random_id" "db_name_suffix" {
  byte_length = 4
}

resource "random_password" "db_password" {
  length  = 16
  special = false
}

resource "google_sql_database_instance" "postgres" {
  name             = "${var.project_name}-postgres-${random_id.db_name_suffix.hex}"
  project          = var.project_id
  region           = var.region
  database_version = "POSTGRES_15"

  settings {
    tier = "db-f1-micro" # Small/cost-effective tier for lightweight application database

    ip_configuration {
      ipv4_enabled    = true
      private_network = null # Set up VPC connection here if deploying inside a private VPC
    }
  }

  deletion_protection = false # Set to true for production systems to prevent accidental deletion
}

resource "google_sql_database" "dementia_care_db" {
  name     = "dementia_care"
  instance = google_sql_database_instance.postgres.name
  project  = var.project_id
}

resource "google_sql_user" "db_user" {
  name     = "dementia_admin"
  instance = google_sql_database_instance.postgres.name
  project  = var.project_id
  password = random_password.db_password.result
}

# ==============================================================================
# Google Secret Manager Configuration
# ==============================================================================

resource "google_secret_manager_secret" "db_password" {
  secret_id = "${var.project_name}-db-password"
  project   = var.project_id
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "db_password_version" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}

resource "google_secret_manager_secret" "gemini_api_key" {
  secret_id = "${var.project_name}-gemini-api-key"
  project   = var.project_id
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "gemini_api_key_version" {
  secret      = google_secret_manager_secret.gemini_api_key.id
  secret_data = var.gemini_api_key
}

resource "google_secret_manager_secret" "user_api_key" {
  secret_id = "${var.project_name}-user-api-key"
  project   = var.project_id
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "user_api_key_version" {
  secret      = google_secret_manager_secret.user_api_key.id
  secret_data = var.user_api_key
}

resource "google_secret_manager_secret" "admin_api_key" {
  secret_id = "${var.project_name}-admin-api-key"
  project   = var.project_id
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "admin_api_key_version" {
  secret      = google_secret_manager_secret.admin_api_key.id
  secret_data = var.admin_api_key
}

resource "google_project_iam_member" "app_sa_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.app_sa.email}"
}

# ==============================================================================
# Backend API Service (FastAPI on Cloud Run)
# ==============================================================================

resource "google_cloud_run_v2_service" "backend_service" {
  name                = "${var.project_name}-backend"
  project             = var.project_id
  location            = var.region
  deletion_protection = false

  template {
    service_account = google_service_account.app_sa.email

    containers {
      image = "gcr.io/${var.project_id}/${var.project_name}-backend:latest"

      ports {
        container_port = 8000
      }

      env {
        name = "GEMINI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.gemini_api_key.id
            version = "latest"
          }
        }
      }

      env {
        name = "USER_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.user_api_key.id
            version = "latest"
          }
        }
      }

      env {
        name = "ADMIN_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.admin_api_key.id
            version = "latest"
          }
        }
      }

      env {
        name  = "DB_USER"
        value = google_sql_user.db_user.name
      }

      env {
        name = "DB_PASSWORD"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.db_password.id
            version = "latest"
          }
        }
      }

      env {
        name  = "DB_HOST"
        value = "/cloudsql/${google_sql_database_instance.postgres.connection_name}"
      }

      env {
        name  = "DB_NAME"
        value = google_sql_database.dementia_care_db.name
      }

      env {
        name  = "VERTEX_SEARCH_PROJECT_ID"
        value = var.project_id
      }

      env {
        name  = "VERTEX_SEARCH_LOCATION"
        value = "global"
      }

      env {
        name  = "VERTEX_SEARCH_DATASTORE_ID"
        value = "dementia-care-guidelines"
      }

      env {
        name  = "VERTEX_PATIENT_DATASTORE_ID"
        value = "dementia-care-patients"
      }

      # Cloud SQL Auth Proxy sidecar connection configuration
      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }
    }

    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [google_sql_database_instance.postgres.connection_name]
      }
    }
  }

  depends_on = [
    google_project_iam_member.app_sa_secret_accessor,
    google_secret_manager_secret_version.gemini_api_key_version,
    google_secret_manager_secret_version.user_api_key_version,
    google_secret_manager_secret_version.admin_api_key_version,
    google_secret_manager_secret_version.db_password_version
  ]
}

resource "google_cloud_run_service_iam_member" "backend_invoker" {
  location = google_cloud_run_v2_service.backend_service.location
  project  = var.project_id
  service  = google_cloud_run_v2_service.backend_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ==============================================================================
# MCP Service (FastMCP on Cloud Run)
# ==============================================================================

resource "google_cloud_run_v2_service" "mcp_service" {
  name                = "${var.project_name}-mcp"
  project             = var.project_id
  location            = var.region
  deletion_protection = false

  template {
    service_account = google_service_account.app_sa.email

    containers {
      image = "gcr.io/${var.project_id}/${var.project_name}-mcp:latest"

      ports {
        container_port = 8002
      }

      env {
        name = "GEMINI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.gemini_api_key.id
            version = "latest"
          }
        }
      }

      env {
        name  = "DB_USER"
        value = google_sql_user.db_user.name
      }

      env {
        name = "DB_PASSWORD"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.db_password.id
            version = "latest"
          }
        }
      }

      env {
        name  = "DB_HOST"
        value = "/cloudsql/${google_sql_database_instance.postgres.connection_name}"
      }

      env {
        name  = "DB_NAME"
        value = google_sql_database.dementia_care_db.name
      }

      env {
        name  = "VERTEX_SEARCH_PROJECT_ID"
        value = var.project_id
      }

      env {
        name  = "VERTEX_SEARCH_LOCATION"
        value = "global"
      }

      env {
        name  = "VERTEX_SEARCH_DATASTORE_ID"
        value = "dementia-care-guidelines"
      }

      env {
        name  = "VERTEX_PATIENT_DATASTORE_ID"
        value = "dementia-care-patients"
      }

      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }
    }

    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [google_sql_database_instance.postgres.connection_name]
      }
    }
  }

  depends_on = [
    google_project_iam_member.app_sa_secret_accessor,
    google_secret_manager_secret_version.gemini_api_key_version,
    google_secret_manager_secret_version.db_password_version
  ]
}

resource "google_cloud_run_service_iam_member" "mcp_invoker" {
  location = google_cloud_run_v2_service.mcp_service.location
  project  = var.project_id
  service  = google_cloud_run_v2_service.mcp_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ==============================================================================================
# Frontend UI Service (React SPA on Cloud Run)
# ==============================================================================

resource "google_cloud_run_v2_service" "frontend_service" {
  name                = "${var.project_name}-frontend"
  project             = var.project_id
  location            = var.region
  deletion_protection = false

  template {
    containers {
      image = "gcr.io/${var.project_id}/${var.project_name}-frontend:latest"

      ports {
        container_port = 80
      }

      env {
        name  = "VITE_BACKEND_URL"
        value = google_cloud_run_v2_service.backend_service.uri
      }
    }
  }
}

resource "google_cloud_run_service_iam_member" "frontend_invoker" {
  location = google_cloud_run_v2_service.frontend_service.location
  project  = var.project_id
  service  = google_cloud_run_v2_service.frontend_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ==============================================================================
# Outputs
# ==============================================================================

output "backend_url" {
  description = "The URL of the Backend Cloud Run service"
  value       = google_cloud_run_v2_service.backend_service.uri
}

output "frontend_url" {
  description = "The URL of the Frontend Cloud Run service"
  value       = google_cloud_run_v2_service.frontend_service.uri
}

output "mcp_url" {
  description = "The URL of the MCP Cloud Run service"
  value       = google_cloud_run_v2_service.mcp_service.uri
}
