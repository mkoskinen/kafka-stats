# Kafka service
resource "aiven_service" "statskafka" {
  project                 = aiven_project.statsproject.project
  cloud_name              = var.aiven_region
  plan                    = "startup-2"
  service_name            = "${var.environment}-statskafka"
  service_type            = "kafka"
  maintenance_window_dow  = "monday"
  maintenance_window_time = "10:00:00"
  kafka_user_config {
    kafka_connect = false
    kafka_rest    = false
    kafka_version = "2.3"
    kafka {
      group_max_session_timeout_ms = 70000
      log_retention_bytes          = 1000000000
    }
  }
}

# Topic for Kafka
resource "aiven_kafka_topic" "stats_topic" {
  project         = aiven_project.statsproject.project
  service_name    = aiven_service.statskafka.service_name
  topic_name      = "stats_topic"
  partitions      = 3
  replication     = 2
  retention_bytes = 1000000000
}

# Consumer user for Kafka
resource "aiven_service_user" "kafka_consumer" {
  project      = aiven_project.statsproject.project
  service_name = aiven_service.statskafka.service_name
  username     = "kafka_consumer"
}

# ACL for Kafka consumer
resource "aiven_kafka_acl" "kafka_c_acl" {
  project      = aiven_project.statsproject.project
  service_name = aiven_service.statskafka.service_name
  username     = "kafka_*"
  permission   = "read"
  topic        = "*"
}

# Producer user for Kafka
resource "aiven_service_user" "kafka_producer" {
  project      = aiven_project.statsproject.project
  service_name = aiven_service.statskafka.service_name
  username     = "kafka_producer"
}

# ACL for Kafka producer
resource "aiven_kafka_acl" "kafka_p_acl" {
  project      = aiven_project.statsproject.project
  service_name = aiven_service.statskafka.service_name
  username     = "kafka_producer"
  permission   = "write"
  topic        = "*"
}

