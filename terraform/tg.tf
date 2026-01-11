resource "aws_lb_target_group" "mc_app_tg" {
  name            = "${local.name_prefix}-tg"
  target_type     = "ip"
  port            = 8000
  protocol        = "HTTP"
  vpc_id          = module.vpc.vpc_id
  ip_address_type = "ipv4"

  health_check {
    enabled             = true
    healthy_threshold   = 4
    interval            = 30
    matcher             = "200-299"
    path                = "/health/"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 20
    unhealthy_threshold = 4
  }

  tags = {
    Name = "${local.name_prefix}-tg"
  }
}
