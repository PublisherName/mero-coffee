data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_secretsmanager_secret" "mc_app_secret" {
  name = var.app_secrets_name
}

data "aws_secretsmanager_secret_version" "mc_app_secret_current" {
  secret_id = data.aws_secretsmanager_secret.mc_app_secret.id
}

data "aws_secretsmanager_secret_version" "rds_master_password" {
  secret_id = module.db.db_instance_master_user_secret_arn
}

data "aws_secretsmanager_secret" "ghcr_token" {
  name = var.ghcr_credentials_name
}
