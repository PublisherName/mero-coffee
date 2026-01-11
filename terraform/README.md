# MeroCoffee Terraform Infrastructure

This directory contains Terraform configuration for deploying MeroCoffee on AWS.

## Architecture

- **VPC**: Multi-AZ VPC with public, private, and database subnets
- **ECS Fargate**: Containerized application deployment
- **RDS PostgreSQL**: Managed database with automated backups
- **Application Load Balancer**: HTTP/HTTPS traffic distribution
- **CloudWatch**: Centralized logging and monitoring
- **Secrets Manager**: Secure credential management

## File Structure

```
terraform/
├── terraform.tf          # Provider and backend configuration
├── variables.tf          # Input variables
├── locals.tf            # Local values and common tags
├── data.tf              # Data sources
├── outputs.tf           # Output values
├── vpc.tf               # VPC and networking
├── security_group.tf    # Security groups
├── database.tf          # RDS PostgreSQL
├── role.tf              # IAM roles and policies
├── cluster.tf           # ECS cluster
├── task.tf              # ECS task definition
├── alb.tf               # Application Load Balancer
├── tg.tf                # Target group
└── terraform.tfvars.example  # Example variables file
```

## Prerequisites

1. **AWS CLI** configured with appropriate credentials
2. **Terraform** >= 1.14
3. **AWS Secrets Manager** secrets created:
   - `mero-coffee-application-secret` - Application configuration
   - `ghcr-credentials` - GitHub Container Registry credentials

## Setup

1. **Copy example variables:**
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

2. **Edit terraform.tfvars** with your values

3. **Initialize Terraform:**
   ```bash
   terraform init
   ```

4. **Review the plan:**
   ```bash
   terraform plan
   ```

5. **Apply the configuration:**
   ```bash
   terraform apply
   ```

## Configuration

### Variables

Key variables you can customize in `terraform.tfvars`:

- `aws_region` - AWS region (default: ap-south-1)
- `project_name` - Project name prefix (default: mero-coffee)
- `environment` - Environment name (default: prod)
- `db_instance_class` - RDS instance type (default: db.t3.micro)
- `ecs_task_cpu` - ECS task CPU units (default: 2048)
- `ecs_task_memory` - ECS task memory in MB (default: 4096)
- `app_image` - Docker image URL

### Remote State (Optional)

Uncomment the backend configuration in `terraform.tf` to use S3 for remote state:

```hcl
backend "s3" {
  bucket         = "merocoffee-terraform-state"
  key            = "prod/terraform.tfstate"
  region         = "ap-south-1"
  encrypt        = true
  dynamodb_table = "terraform-state-lock"
}
```

## Outputs

After applying, Terraform will output:

- `vpc_id` - VPC identifier
- `alb_dns_name` - Load balancer DNS name
- `ecs_cluster_name` - ECS cluster name
- `db_endpoint` - RDS endpoint (sensitive)

## Security

- All resources use security groups with least-privilege access
- Database credentials managed via AWS Secrets Manager
- RDS in private subnets with no public access
- Automatic password rotation enabled
- CloudWatch logging enabled

## Cost Optimization

For development/testing:
- Set `db_instance_class = "db.t3.micro"`
- Set `ecs_task_cpu = "256"` and `ecs_task_memory = "512"`
- Use `single_nat_gateway = true` (already configured)

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

**Warning:** This will delete all resources including the database. Ensure you have backups if needed.

## Troubleshooting

### Common Issues

1. **Secret not found**: Ensure secrets exist in AWS Secrets Manager
2. **Insufficient permissions**: Check IAM permissions for Terraform user
3. **Resource limits**: Verify AWS service quotas in your region
4. **Deprecation warnings from VPC module**: These are harmless warnings from the upstream module and don't affect functionality

## Next Steps

After infrastructure is deployed:

1. Create an ECS service to run tasks
2. Configure Route53 DNS records pointing to ALB
3. Set up SSL/TLS certificate in ACM
4. Configure HTTPS listener on ALB
5. Set up CloudWatch alarms for monitoring
