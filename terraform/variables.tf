### Variables
# Aiven

variable "aiven_api_token" {}
variable "aiven_card_id" {}
variable "aiven_project_name" {
  default = "dev-metrics"
}

variable "aiven_region" {
  default = "google-europe-north1"
}

# AWS
variable "aws_region" {
  default = "eu-north-1"
}

variable "environment" {
  default = "dev"
}

variable "project" {
  default = "metrics"
}