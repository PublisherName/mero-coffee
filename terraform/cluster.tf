resource "aws_ecs_cluster" "mc_ecs_cluster" {
  name = "mc-ecs-cluster"

  tags = {
    Name = "MeroCoffeeCluster"
  }
}

output "ecs_cluster_arn" {
  description = "ECS Cluster ARN"
  value       = aws_ecs_cluster.mc_ecs_cluster.arn
}

output "ecs_cluster_id" {
  description = "ECS Cluster ID"
  value       = aws_ecs_cluster.mc_ecs_cluster.id
}
