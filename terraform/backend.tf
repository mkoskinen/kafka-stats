terraform {
  backend "s3" {
    bucket         = "mkoskinen-stats-tf"
    region         = "eu-north-1"
    key            = "dev/terraform.tfstate"
    encrypt        = "true"
    dynamodb_table = "terraform-state-locks"
  }
}

resource "aws_dynamodb_table" "terraform-state-lock" {
  name           = "terraform-state-locks"
  hash_key       = "LockID"
  read_capacity  = 5
  write_capacity = 5

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    project   = var.project
    terraform = "true"
  }
}
