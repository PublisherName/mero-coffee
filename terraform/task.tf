resource "aws_cloudwatch_log_group" "mc_app" {
  name              = "/ecs/mero-coffee-app"
  retention_in_days = 7

  tags = {
    Name = "MeroCoffeeAppLogs"
  }
}

resource "aws_ecs_task_definition" "mc_task_definition" {
  family                   = "mero-coffee-task-definition"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "2048"
  memory                   = "4096"

  execution_role_arn = aws_iam_role.mc_ecs_task_execution_role.arn
  task_role_arn      = aws_iam_role.mc_ecs_task_execution_role.arn

  container_definitions = jsonencode([{
    name  = "mero-coffee-app"
    image = "ghcr.io/publishername/merocoffee:develop"

    repositoryCredentials = {
      credentialsParameter = data.aws_secretsmanager_secret.ghcr_token.arn,
    }

    essential = true

    portMappings = [{
      containerPort = 8000
      hostPort      = 8000
      protocol      = "tcp"
    }]

    ulimits = [
      { name = "nofile", softLimit = 65535, hardLimit = 65535 },
      { name = "nproc", softLimit = 1024, hardLimit = 1024 }
    ]

    secrets = [
      { name = "SERVER_ENVIRONMENT", valueFrom = "${data.aws_secretsmanager_secret.mc_app_secret.arn}:SERVER_ENVIRONMENT::" },
      { name = "DJANGO_SECRET_KEY", valueFrom = "${data.aws_secretsmanager_secret.mc_app_secret.arn}:DJANGO_SECRET_KEY::" },
      { name = "DJANGO_ALLOWED_HOSTS", valueFrom = "${data.aws_secretsmanager_secret.mc_app_secret.arn}:DJANGO_ALLOWED_HOSTS::" },
      { name = "SITE_BASE_URL", valueFrom = "${data.aws_secretsmanager_secret.mc_app_secret.arn}:SITE_BASE_URL::" },

      { name = "DATABASE_URL", valueFrom = "${data.aws_secretsmanager_secret.mc_app_secret.arn}:DATABASE_URL::" }, #TODO: REMOVE THIS

      { name = "DB_HOST", valueFrom = "${data.aws_secretsmanager_secret.mc_app_secret.arn}:DB_HOST::" },
      { name = "DB_PORT", valueFrom = "${data.aws_secretsmanager_secret.mc_app_secret.arn}:DB_PORT::" },
      { name = "DB_NAME", valueFrom = "${data.aws_secretsmanager_secret.mc_app_secret.arn}:DB_NAME::" },
      { name = "DB_USER", valueFrom = "${module.db.db_instance_master_user_secret_arn}:username::" },
      { name = "DB_PASSWORD", valueFrom = "${module.db.db_instance_master_user_secret_arn}:password::" },

      { name = "CACHE_URL", valueFrom = "${data.aws_secretsmanager_secret.mc_app_secret.arn}:CACHE_URL::" },
      { name = "SMTP_URL", valueFrom = "${data.aws_secretsmanager_secret.mc_app_secret.arn}:SMTP_URL::" },
      { name = "TOKEN_SALT", valueFrom = "${data.aws_secretsmanager_secret.mc_app_secret.arn}:TOKEN_SALT::" },

      { name = "TURNSTILE_SITEKEY", valueFrom = "${data.aws_secretsmanager_secret.mc_app_secret.arn}:TURNSTILE_SITEKEY::" },
      { name = "TURNSTILE_SECRET", valueFrom = "${data.aws_secretsmanager_secret.mc_app_secret.arn}:TURNSTILE_SECRET::" },
      { name = "USE_CELERY", valueFrom = "${data.aws_secretsmanager_secret.mc_app_secret.arn}:USE_CELERY::" },

      { name = "ENABLE_SENTRY", valueFrom = "${data.aws_secretsmanager_secret.mc_app_secret.arn}:ENABLE_SENTRY::" },
      { name = "SENTRY_DSN", valueFrom = "${data.aws_secretsmanager_secret.mc_app_secret.arn}:SENTRY_DSN::" },
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.mc_app.name
        awslogs-region        = "ap-south-1"
        awslogs-stream-prefix = "django"
        awslogs-create-group  = "true"
      }
    }

    healthCheck = {
      command = [
        "CMD-SHELL",
        "curl -f http://localhost:8000/health/ || exit 1"
      ]
      interval    = 30
      timeout     = 10
      retries     = 3
      startPeriod = 60
    }

    readonlyRootFilesystem = false
  }])

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  tags = {
    Name = "MeroCoffeeDjangoTask"
  }
}

output "ecs_task_definition_arn" {
  description = "Django Task Definition ARN (use in ECS Service)"
  value       = aws_ecs_task_definition.mc_task_definition.arn
}

output "ecs_task_definition_family" {
  description = "Task Definition Family"
  value       = aws_ecs_task_definition.mc_task_definition.family
}
