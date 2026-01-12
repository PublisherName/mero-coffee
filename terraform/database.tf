module "db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 6.0"

  identifier           = "${local.name_prefix}db"
  engine               = "postgres"
  engine_version       = "17.2"
  family               = "postgres17"
  major_engine_version = "17.2"

  instance_class    = var.db_instance_class
  allocated_storage = var.db_allocated_storage
  storage_type      = "gp2"
  storage_encrypted = true

  db_name  = "merocoffeedb"
  username = "postgres"
  port     = 5432

  availability_zone      = var.availability_zones[0]
  create_db_subnet_group = false
  vpc_security_group_ids = [aws_security_group.mc_data_sg.id]
  db_subnet_group_name   = module.vpc.database_subnet_group_name
  publicly_accessible    = false

  max_allocated_storage = 0
  create_db_instance    = true

  manage_master_user_password                            = true
  master_user_password_rotation_automatically_after_days = 30

  maintenance_window      = "Mon:00:00-Mon:03:00"
  backup_window           = "03:00-06:00"
  backup_retention_period = 0

  monitoring_interval    = 30
  create_monitoring_role = true
  monitoring_role_name   = "${local.name_prefix}-rds-monitoring-role"

  multi_az                     = false
  deletion_protection          = false
  skip_final_snapshot          = true
  allow_major_version_upgrade  = false
  auto_minor_version_upgrade   = true
  performance_insights_enabled = true

  parameters = [
    { name = "log_connections", value = "1" },
    { name = "rds.log_retention_period", value = "1440" }
  ]

  tags = {
    Name = "${local.name_prefix}-db"
  }
}
