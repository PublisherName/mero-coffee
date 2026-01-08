# Load balancer security group
resource "aws_security_group" "mc-alb-sg" {
  name        = "mc-alb-sg"
  description = "Security group for load balancer"
  vpc_id      = module.vpc.vpc_id

  tags = {
    Name = "mc-alb-sg"
  }
}

resource "aws_vpc_security_group_ingress_rule" "alb_allow_http" {
  security_group_id = aws_security_group.mc-alb-sg.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 80
  ip_protocol       = "tcp"
  to_port           = 80
}

resource "aws_vpc_security_group_ingress_rule" "alb_allow_https" {
  security_group_id = aws_security_group.mc-alb-sg.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 443
  ip_protocol       = "tcp"
  to_port           = 443
}


resource "aws_vpc_security_group_egress_rule" "alb_allow_all_traffic_ipv4" {
  security_group_id = aws_security_group.mc-alb-sg.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}


# Application security group
resource "aws_security_group" "mc-app-sg" {
  name        = "mc-app-sg"
  description = "Security group for application"
  vpc_id      = module.vpc.vpc_id

  tags = {
    Name = "mc-app-sg"
  }
}

resource "aws_vpc_security_group_ingress_rule" "app_allow_http" {
  security_group_id            = aws_security_group.mc-app-sg.id
  from_port                    = 80
  to_port                      = 80
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.mc-alb-sg.id
  description                  = "HTTP from ALB SG"
}

resource "aws_vpc_security_group_egress_rule" "app_allow_all_traffic_ipv4" {
  security_group_id = aws_security_group.mc-app-sg.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}


# Data Security Group
resource "aws_security_group" "mc-data-sg" {
  name        = "mc-data-sg"
  description = "Security group for data"
  vpc_id      = module.vpc.vpc_id

  tags = {
    Name = "mc-data-sg"
  }
}

resource "aws_vpc_security_group_ingress_rule" "data_allow_http" {
  security_group_id            = aws_security_group.mc-data-sg.id
  from_port                    = 5432
  to_port                      = 5432
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.mc-app-sg.id
  description                  = "Postgres from APP SG"
}

resource "aws_vpc_security_group_ingress_rule" "data_allow_lambda_rotation" {
  security_group_id            = aws_security_group.mc-data-sg.id
  from_port                    = 5432
  to_port                      = 5432
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.mc-data-sg.id
  description                  = "Postgres from Lambda Rotation"
}

# Outputs
output "alb_security_group_id" {
  description = "MeroCoffee ALB Security Group ID"
  value       = aws_security_group.mc-alb-sg.id
}

output "app_security_group_id" {
  description = "MeroCoffee Application Security Group ID"
  value       = aws_security_group.mc-app-sg.id
}

output "data_security_group_id" {
  description = "MeroCoffee Data (Postgres) Security Group ID"
  value       = aws_security_group.mc-data-sg.id
}
