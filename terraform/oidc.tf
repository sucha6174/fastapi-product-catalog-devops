# ==========================================
# GitHub Actions OIDC Provider & Least-Privilege IAM Role
# ==========================================

# OpenID Connect Provider for GitHub Actions (conditionally created)
resource "aws_iam_openid_connect_provider" "github" {
  count           = var.enable_github_oidc ? 1 : 0
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1", "1c58761d24ed748f41a20a918132f881a4430d13"]

  tags = {
    Name = "${var.project_name}-github-oidc-provider"
  }
}

# IAM Role assumed by GitHub Actions via OIDC
resource "aws_iam_role" "github_actions_oidc" {
  count = var.enable_github_oidc ? 1 : 0
  name  = "${var.project_name}-${var.environment}-github-actions-oidc-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.github[0].arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:${var.github_repo}:*"
          }
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-github-actions-oidc-role"
  }
}

# Least-Privilege Policy for ECR and ECS
resource "aws_iam_policy" "github_actions_policy" {
  count       = var.enable_github_oidc ? 1 : 0
  name        = "${var.project_name}-${var.environment}-github-actions-policy"
  description = "Allows GitHub Actions runner to push images to ECR and update ECS service"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ECRAuthToken"
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken"
        ]
        Resource = "*"
      },
      {
        Sid    = "ECRImagePush"
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload"
        ]
        Resource = aws_ecr_repository.app.arn
      },
      {
        Sid    = "ECSDeployment"
        Effect = "Allow"
        Action = [
          "ecs:UpdateService",
          "ecs:DescribeServices"
        ]
        Resource = aws_ecs_service.app.id
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "github_actions_attach" {
  count      = var.enable_github_oidc ? 1 : 0
  role       = aws_iam_role.github_actions_oidc[0].name
  policy_arn = aws_iam_policy.github_actions_policy[0].arn
}
