# ==========================================
# Terraform Infrastructure Outputs
# ==========================================

output "rds_endpoint" {
  description = "Connection endpoint address and port for the RDS PostgreSQL database"
  value       = aws_db_instance.app_db.endpoint
}

output "rds_address" {
  description = "Hostname of the RDS PostgreSQL database"
  value       = aws_db_instance.app_db.address
}

output "ecr_repository_url" {
  description = "URI of the Amazon ECR Docker repository"
  value       = aws_ecr_repository.app.repository_url
}

output "ecs_cluster_name" {
  description = "Name of the ECS Fargate cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "Name of the ECS Fargate service"
  value       = aws_ecs_service.app.name
}

output "api_public_ip_command" {
  description = "AWS CLI command to retrieve the running Fargate task's dynamic public IP"
  value       = "aws ec2 describe-network-interfaces --network-interface-ids $(aws ecs describe-tasks --cluster ${aws_ecs_cluster.main.name} --tasks $(aws ecs list-tasks --cluster ${aws_ecs_cluster.main.name} --service-name ${aws_ecs_service.app.name} --query 'taskArns[0]' --output text) --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' --output text) --query 'NetworkInterfaces[0].Association.PublicIp' --output text"
}

output "api_access_instructions" {
  description = "Instructions for testing and accessing the deployed FastAPI application"
  value       = "Once the ECS task is in RUNNING state, execute the command in 'api_public_ip_command' to obtain the public IP, then access the API at http://<PUBLIC_IP>:8000/docs"
}

output "github_actions_oidc_role_arn" {
  description = "IAM Role ARN for GitHub Actions OIDC authentication (set as AWS_ROLE_TO_ASSUME secret)"
  value       = var.enable_github_oidc ? aws_iam_role.github_actions_oidc[0].arn : "OIDC provisioning disabled (set enable_github_oidc = true to enable)"
}
