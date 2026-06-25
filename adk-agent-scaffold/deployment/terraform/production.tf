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
# Managed Database (Google Cloud SQL PostgreSQL)
# ==============================================================================

resource "random_id" "db_name_suffix" {
  byte_length = 4
}

resource "google_sql_database_instance" "postgres" {
  name             = "${var.project_name}-postgres-${random_id.db_name_suffix.hex}"
  project          = var.prod_project_id
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
  project  = var.prod_project_id
}

resource "google_sql_user" "db_user" {
  name     = "dementia_admin"
  instance = google_sql_database_instance.postgres.name
  project  = var.prod_project_id
  password = "SecureDbPassword2026!" # Should be stored in Secret Manager in production
}

# ==============================================================================
# RAG Service (Standalone ChromaDB Server on Cloud Run)
# ==============================================================================

resource "google_cloud_run_v2_service" "rag_service" {
  name     = "${var.project_name}-rag"
  project  = var.prod_project_id
  location = var.region

  template {
    containers {
      image = "chromadb/chroma:0.4.24"

      ports {
        container_port = 8000
      }

      env {
        name  = "IS_PERSISTENT"
        value = "TRUE"
      }
    }
  }
}

# Allow internal/unauthenticated invocation on RAG service (secure with IAM in production)
resource "google_cloud_run_service_iam_member" "rag_invoker" {
  location = google_cloud_run_v2_service.rag_service.location
  project  = var.prod_project_id
  service  = google_cloud_run_v2_service.rag_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ==============================================================================
# Backend API Service (FastAPI on Cloud Run)
# ==============================================================================

resource "google_cloud_run_v2_service" "backend_service" {
  name     = "${var.project_name}-backend"
  project  = var.prod_project_id
  location = var.region

  template {
    containers {
      image = "gcr.io/${var.prod_project_id}/${var.project_name}-backend:latest"

      ports {
        container_port = 8000
      }

      env {
        name  = "GEMINI_API_KEY"
        value = "YOUR_GEMINI_API_KEY" # Reference secret manager in production
      }

      env {
        name  = "DATABASE_URL"
        value = "postgresql://${google_sql_user.db_user.name}:${google_sql_user.db_user.password}@127.0.0.1:5432/${google_sql_database.dementia_care_db.name}"
      }

      env {
        name  = "CHROMA_SERVER_HOST"
        value = replace(google_cloud_run_v2_service.rag_service.uri, "https://", "")
      }

      env {
        name  = "CHROMA_SERVER_PORT"
        value = "443"
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
}

resource "google_cloud_run_service_iam_member" "backend_invoker" {
  location = google_cloud_run_v2_service.backend_service.location
  project  = var.prod_project_id
  service  = google_cloud_run_v2_service.backend_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ==============================================================================
# Frontend UI Service (React SPA on Cloud Run)
# ==============================================================================

resource "google_cloud_run_v2_service" "frontend_service" {
  name     = "${var.project_name}-frontend"
  project  = var.prod_project_id
  location = var.region

  template {
    containers {
      image = "gcr.io/${var.prod_project_id}/${var.project_name}-frontend:latest"

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
  project  = var.prod_project_id
  service  = google_cloud_run_v2_service.frontend_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
