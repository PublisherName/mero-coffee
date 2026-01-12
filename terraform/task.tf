resource "aws_cloudwatch_log_group" "mc_app" {
  name              = "/ecs/${local.name_prefix}-app"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${local.name_prefix}-app-logs"
  }
}

resource "aws_ecs_task_definition" "mc_task_definition" {
  family                   = "${local.name_prefix}-task-definition"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.ecs_task_cpu
  memory                   = var.ecs_task_memory

  execution_role_arn = aws_iam_role.mc_ecs_task_execution_role.arn
  task_role_arn      = aws_iam_role.mc_ecs_task_execution_role.arn

  container_definitions = jsonencode([{
    name  = "${local.name_prefix}-app"
    image = var.app_image

    repositoryCredentials = {
      credentialsParameter = data.aws_secretsmanager_secret.ghcr_token.arn
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
      { name = "DATABASE_URL", valueFrom = "${data.aws_secretsmanager_secret.mc_app_secret.arn}:DATABASE_URL::" },
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
        awslogs-region        = var.aws_region
        awslogs-stream-prefix = "django"
        awslogs-create-group  = "true"
      }
    }

    healthCheck = {
      command = [
        "CMD-SHELL",
        "curl -f http://127.0.0.1:8000/health/ || exit 1"
      ]
      interval    = 30
      timeout     = 20
      retries     = 10
      startPeriod = 120
    }

    readonlyRootFilesystem = false
  }])

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  tags = {
    Name = "${local.name_prefix}-django-task"
  }

  depends_on = [aws_secretsmanager_secret_version.mc_app_secret_updated]
}
