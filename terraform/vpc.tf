provider "aws" {
  region = "ap-south-1"
}

data "aws_availability_zone" "az_a" {
  name = "ap-south-1a"
}

data "aws_availability_zone" "az_b" {
  name = "ap-south-1b"
}

locals {
  azs = [data.aws_availability_zone.az_a.name, data.aws_availability_zone.az_b.name]
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.8"

  name = "mero-coffee-vpc"
  cidr = "10.0.0.0/16"

  azs = local.azs

  public_subnets   = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets  = ["10.0.10.0/24", "10.0.11.0/24"]
  database_subnets = ["10.0.20.0/24", "10.0.21.0/24"]

  create_igw = true

  enable_nat_gateway                = true
  single_nat_gateway                = true
  one_nat_gateway_per_az            = false
  create_database_nat_gateway_route = true

  enable_dns_hostnames = true
  enable_dns_support   = true

  create_database_subnet_group       = true
  create_database_subnet_route_table = true
  database_subnet_group_name         = "mc-db-subnet-group"


  # Resources Names
  public_subnet_names = [
    "mc-public-sn-ap-south-1a",
    "mc-public-sn-ap-south-1b"
  ]
  public_route_table_tags = {
    Name = "mc-public-rt"
  }

  private_subnet_names = [
    "mc-app-sn-ap-south-1a",
    "mc-app-sn-ap-south-1b"
  ]
  private_route_table_tags = {
    Name = "mc-app-rt"
  }

  database_subnet_names = [
    "mc-data-sn-ap-south-1a",
    "mc-data-sn-ap-south-1b"
  ]
  database_route_table_tags = {
    Name = "mc-data-rt"
  }

  nat_gateway_tags = {
    Name = "mc-nat-gw"
  }
  igw_tags = {
    Name = "mc-igw"
  }

}

output "vpc_id" {
  description = "MeroCoffee VPC ID"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "Public subnet IDs (ALBs, etc.)"
  value       = module.vpc.public_subnets
}

output "private_app_subnet_ids" {
  description = "Private app subnet IDs (ECS tasks)"
  value       = module.vpc.private_subnets
}

output "database_subnet_ids" {
  description = "Database subnet IDs (RDS)"
  value       = module.vpc.database_subnets
}

output "nat_public_ip" {
  description = "NAT Gateway public IP"
  value       = module.vpc.nat_public_ips[0]
}

output "igw_id" {
  description = "Internet Gateway ID"
  value       = module.vpc.igw_id
}

output "database_subnet_group_name" {
  description = "RDS subnet group name"
  value       = module.vpc.database_subnet_group_name
}
