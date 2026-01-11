resource "aws_ecs_service" "mc_service" {
  name            = "${local.name_prefix}-service"
  cluster         = aws_ecs_cluster.mc_ecs_cluster.id
  task_definition = aws_ecs_task_definition.mc_task_definition.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = module.vpc.private_subnets
    security_groups  = [aws_security_group.mc_app_sg.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.mc_app_tg.arn
    container_name   = "${local.name_prefix}-app"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.mc_http_redirect, aws_lb_listener.mc_https]

  tags = {
    Name = "${local.name_prefix}-service"
  }
}
