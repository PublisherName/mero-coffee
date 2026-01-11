#TODO: Remove the wildcard
resource "aws_secretsmanager_secret_version" "mc_app_secret_updated" {
  secret_id = data.aws_secretsmanager_secret.mc_app_secret.id
  secret_string = jsonencode(merge(
    jsondecode(data.aws_secretsmanager_secret_version.mc_app_secret_current.secret_string),
    {
      DATABASE_URL         = "postgresql://${module.db.db_instance_username}:${jsondecode(data.aws_secretsmanager_secret_version.rds_master_password.secret_string)["password"]}@${module.db.db_instance_address}:${module.db.db_instance_port}/${module.db.db_instance_name}"
      DJANGO_ALLOWED_HOSTS = var.domain_name != "" ? "${var.domain_name},.${var.domain_name},*" : "*"
      ALLOWED_CIDR_NETS    = "${var.vpc_cidr}"
      SITE_BASE_URL        = var.domain_name != "" ? "https://${var.domain_name}" : "http://${aws_lb.mc_alb.dns_name}"
    }
  ))
  depends_on = [module.db, aws_lb.mc_alb]
}
