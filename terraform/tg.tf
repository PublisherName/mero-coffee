resource "aws_lb_target_group" "mc_app_tg" {
  name            = "mc-tg"
  target_type     = "ip"
  port            = 80
  protocol        = "HTTP"
  vpc_id          = module.vpc.vpc_id
  ip_address_type = "ipv4"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 50
    matcher             = "200-299"
    path                = "/health/"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 3
  }
}

output "target_group_arn" {
  description = "ALB Target Group ARN for ECS"
  value       = aws_lb_target_group.mc_app_tg.arn
}
