resource "aws_ecs_service" "mc_celery_service" {
  name            = "${local.name_prefix}-celery-service"
  cluster         = aws_ecs_cluster.mc_ecs_cluster.id
  task_definition = aws_ecs_task_definition.mc_celery_task_definition.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = module.vpc.private_subnets
    security_groups  = [aws_security_group.mc_app_sg.id]
    assign_public_ip = false
  }

  tags = {
    Name = "${local.name_prefix}-celery-service"
  }

  lifecycle {
    ignore_changes = [desired_count]
  }
}
