data "aws_secretsmanager_secret" "mc-app-secret" {
  name = "mero-coffee-application-secret"
}

data "aws_secretsmanager_secret" "ghcr_token" {
  name = "ghcr-credentials"
}

resource "aws_iam_policy" "mc_ecs_secrets" {
  name        = "mc_ecs_secret_policy"
  description = "Access RDS password + Application Secret + Ghcr.io secret"

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
          data.aws_secretsmanager_secret.mc-app-secret.arn,
          data.aws_secretsmanager_secret.ghcr_token.arn,
        ]
      },
    ]
  })

  tags = {
    Name = "mc_ecs_secret_policy"
  }
}

resource "aws_iam_role" "mc_ecs_task_execution_role" {
  name = "mc-ecs-task-role"

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
    Name = "MeroCoffeeEcsTask"
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

output "ecs_task_execution_role_arn" {
  description = "ECS Task Execution Role ARN"
  value       = aws_iam_role.mc_ecs_task_execution_role.arn
}
