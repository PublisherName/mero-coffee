resource "aws_iam_policy" "mc_ecs_secrets" {
  name        = "${local.name_prefix}-ecs-secret-policy"
  description = "Access RDS password + Application Secret + GHCR secret"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
          "ssm:GetParameters",
          "ssm:GetParameter",
          "ssm:DescribeParameters"
        ]
        Resource = [
          module.db.db_instance_master_user_secret_arn,
          data.aws_secretsmanager_secret.mc_app_secret.arn,
          data.aws_secretsmanager_secret.ghcr_token.arn,
        ]
      },
    ]
  })

  tags = {
    Name = "${local.name_prefix}-ecs-secret-policy"
  }
}

resource "aws_iam_policy" "mc_ecs_log" {
  name        = "${local.name_prefix}-ecs-log-policy"
  description = "Access log groups"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:CreateLogGroup",
          "logs:PutLogEvents"
        ]
        Resource = [
          "arn:aws:logs:${var.aws_region}:*:log-group:/ecs/*:*",
          "arn:aws:logs:${var.aws_region}:*:log-group:/aws/ecs/*"
        ]
      }
    ]
  })

  tags = {
    Name = "${local.name_prefix}-ecs-log-policy"
  }
}

resource "aws_iam_role" "mc_ecs_task_execution_role" {
  name = "${local.name_prefix}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })

  tags = {
    Name = "${local.name_prefix}-ecs-task-role"
  }
}

resource "aws_iam_role_policy_attachment" "mc_ecs_secret_policy" {
  role       = aws_iam_role.mc_ecs_task_execution_role.name
  policy_arn = aws_iam_policy.mc_ecs_secrets.arn
}

resource "aws_iam_role_policy_attachment" "mc_ecs_task_policy" {
  role       = aws_iam_role.mc_ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "mc_ecs_log_policy" {
  role       = aws_iam_role.mc_ecs_task_execution_role.name
  policy_arn = aws_iam_policy.mc_ecs_log.arn
}
