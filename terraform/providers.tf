provider "aws" {
  region  = "${var.aws_region}"
  version = "~> 2.27"
}

provider "aiven" {
  api_token = "${var.aiven_api_token}"
}
