resource "aws_security_group" "mc_alb_sg" {
  name        = "${local.name_prefix}-alb-sg"
  description = "Security group for load balancer"
  vpc_id      = module.vpc.vpc_id

  tags = {
    Name = "${local.name_prefix}-alb-sg"
  }
}

resource "aws_vpc_security_group_ingress_rule" "alb_allow_http" {
  security_group_id = aws_security_group.mc_alb_sg.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 80
  ip_protocol       = "tcp"
  to_port           = 80
}

resource "aws_vpc_security_group_ingress_rule" "alb_allow_https" {
  security_group_id = aws_security_group.mc_alb_sg.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 443
  ip_protocol       = "tcp"
  to_port           = 443
}

resource "aws_vpc_security_group_egress_rule" "alb_allow_all_traffic_ipv4" {
  security_group_id = aws_security_group.mc_alb_sg.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

resource "aws_security_group" "mc_app_sg" {
  name        = "${local.name_prefix}-app-sg"
  description = "Security group for application"
  vpc_id      = module.vpc.vpc_id

  tags = {
    Name = "${local.name_prefix}-app-sg"
  }
}

resource "aws_vpc_security_group_ingress_rule" "app_allow_http" {
  security_group_id            = aws_security_group.mc_app_sg.id
  from_port                    = 8000
  to_port                      = 8000
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.mc_alb_sg.id
  description                  = "Port 8000 from ALB SG"
}

resource "aws_vpc_security_group_egress_rule" "app_allow_all_traffic_ipv4" {
  security_group_id = aws_security_group.mc_app_sg.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

resource "aws_security_group" "mc_data_sg" {
  name        = "${local.name_prefix}-data-sg"
  description = "Security group for data"
  vpc_id      = module.vpc.vpc_id

  tags = {
    Name = "${local.name_prefix}-data-sg"
  }
}

resource "aws_vpc_security_group_ingress_rule" "data_allow_postgres" {
  security_group_id            = aws_security_group.mc_data_sg.id
  from_port                    = 5432
  to_port                      = 5432
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.mc_app_sg.id
  description                  = "Postgres from APP SG"
}

resource "aws_vpc_security_group_ingress_rule" "data_allow_lambda_rotation" {
  security_group_id            = aws_security_group.mc_data_sg.id
  from_port                    = 5432
  to_port                      = 5432
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.mc_data_sg.id
  description                  = "Postgres from Lambda Rotation"
}
