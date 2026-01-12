resource "aws_ecs_cluster" "mc_ecs_cluster" {
  name = "${local.name_prefix}-ecs-cluster"

  tags = {
    Name = "${local.name_prefix}-ecs-cluster"
  }
}
