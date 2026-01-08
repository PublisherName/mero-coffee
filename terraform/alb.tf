resource "aws_lb" "mc_alb" {
  name               = "mc-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.mc-alb-sg.id]
  subnets            = module.vpc.public_subnets

  enable_deletion_protection = false

  tags = {
    Name = "mc-alb"
  }
}

resource "aws_lb_listener" "mc_http_redirect" {
  load_balancer_arn = aws_lb.mc_alb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.mc_app_tg.arn
  }
}

output "alb_dns_name" {
  description = "ALB DNS for DNS records"
  value       = aws_lb.mc_alb.dns_name
}

output "alb_zone_id" {
  description = "ALB hosted zone ID for Route53 alias"
  value       = aws_lb.mc_alb.zone_id
}
