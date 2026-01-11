resource "aws_secretsmanager_secret_version" "mc_app_secret_updated" {
  secret_id = data.aws_secretsmanager_secret.mc_app_secret.id
  secret_string = jsonencode(merge(
    jsondecode(data.aws_secretsmanager_secret_version.mc_app_secret_current.secret_string),
    {
      DB_HOST              = module.db.db_instance_address
      DB_PORT              = tostring(module.db.db_instance_port)
      DB_NAME              = module.db.db_instance_name
      DB_USER              = module.db.db_instance_username
      DB_PASSWORD          = jsondecode(data.aws_secretsmanager_secret_version.rds_master_password.secret_string)["password"]
      DJANGO_ALLOWED_HOSTS = "${aws_lb.mc_alb.dns_name},10.0.0.0/16"
      SITE_BASE_URL        = "http://${aws_lb.mc_alb.dns_name}"
    }
  ))
  depends_on = [module.db, aws_lb.mc_alb]
}
