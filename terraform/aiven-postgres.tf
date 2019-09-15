# PostreSQL service
resource "aiven_service" "statsdb" {
  project                 = aiven_project.statsproject.project
  cloud_name              = var.aiven_region
  plan                    = "startup-4"
  service_name            = "${var.environment}-statsdb"
  service_type            = "pg"
  maintenance_window_dow  = "monday"
  maintenance_window_time = "12:00:00"
  pg_user_config {
    pg {
      idle_in_transaction_session_timeout = 900
    }
    pg_version = "10"
  }
}

# PostgreSQL database
resource "aiven_database" "stats" {
  project       = aiven_project.statsproject.project
  service_name  = aiven_service.statsdb.service_name
  database_name = "stats"
}

# PostgreSQL user
resource "aiven_service_user" "stats-server-user" {
  project      = aiven_project.statsproject.project
  service_name = aiven_service.statsdb.service_name
  username     = "${var.environment}-stats"
}
