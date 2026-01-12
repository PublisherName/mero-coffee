module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.8"

  name = "${local.name_prefix}-vpc"
  cidr = var.vpc_cidr
  azs  = var.availability_zones

  public_subnets   = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets  = ["10.0.10.0/24", "10.0.11.0/24"]
  database_subnets = ["10.0.20.0/24", "10.0.21.0/24"]

  create_igw                        = true
  enable_nat_gateway                = true
  single_nat_gateway                = true
  one_nat_gateway_per_az            = false
  create_database_nat_gateway_route = true
  enable_dns_hostnames              = true
  enable_dns_support                = true

  create_database_subnet_group       = true
  create_database_subnet_route_table = true
  database_subnet_group_name         = "${local.name_prefix}-db-subnet-group"

  public_subnet_names = [
    "${local.name_prefix}-public-sn-${var.availability_zones[0]}",
    "${local.name_prefix}-public-sn-${var.availability_zones[1]}"
  ]

  private_subnet_names = [
    "${local.name_prefix}-app-sn-${var.availability_zones[0]}",
    "${local.name_prefix}-app-sn-${var.availability_zones[1]}"
  ]

  database_subnet_names = [
    "${local.name_prefix}-data-sn-${var.availability_zones[0]}",
    "${local.name_prefix}-data-sn-${var.availability_zones[1]}"
  ]

  public_route_table_tags = {
    Name = "${local.name_prefix}-public-rt"
  }

  private_route_table_tags = {
    Name = "${local.name_prefix}-app-rt"
  }

  database_route_table_tags = {
    Name = "${local.name_prefix}-data-rt"
  }

  nat_gateway_tags = {
    Name = "${local.name_prefix}-nat-gw"
  }

  igw_tags = {
    Name = "${local.name_prefix}-igw"
  }
}
