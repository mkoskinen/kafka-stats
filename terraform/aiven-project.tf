resource "aiven_project" "statsproject" {
  project = var.aiven_project_name
  card_id = var.aiven_card_id
}