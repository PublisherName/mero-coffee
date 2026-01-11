output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnets
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.vpc.private_subnets
}

output "database_subnet_ids" {
  description = "Database subnet IDs"
  value       = module.vpc.database_subnets
}

output "alb_dns_name" {
  description = "ALB DNS name"
  value       = aws_lb.mc_alb.dns_name
}

output "alb_zone_id" {
  description = "ALB hosted zone ID"
  value       = aws_lb.mc_alb.zone_id
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.mc_ecs_cluster.name
}

output "ecs_task_definition_arn" {
  description = "ECS task definition ARN"
  value       = aws_ecs_task_definition.mc_task_definition.arn
}

output "db_endpoint" {
  description = "RDS endpoint"
  value       = module.db.db_instance_endpoint
  sensitive   = true
}

output "db_secret_arn" {
  description = "RDS master user secret ARN"
  value       = module.db.db_instance_master_user_secret_arn
  sensitive   = true
}
