data "tls_certificate" "github_actions" {
  url = "https://token.actions.githubusercontent.com"
}

resource "aws_iam_openid_connect_provider" "github_actions" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.github_actions.certificates.0.sha1_fingerprint]
}

resource "aws_iam_role" "github_actions" {
  name        = "GitHubActionsRole"
  description = "IAM Role that a GitHub Actions runner can assume to authenticate with AWS via OIDC."

  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Federated" : aws_iam_openid_connect_provider.github_actions.arn
        },
        "Action" : "sts:AssumeRoleWithWebIdentity",
        "Condition" : {
          "StringLike" : {
            "token.actions.githubusercontent.com:sub" : "repo:KitwareMedical/xray-genius:ref:refs/heads/main",
            "token.actions.githubusercontent.com:aud" : "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  # Inline policy that allows GitHub actions to reboot the EC2 worker
  inline_policy {
    name = "GitHubActionsPolicy"
    policy = jsonencode({
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Sid" : "RebootEC2Worker",
          "Effect" : "Allow",
          "Resource" : "*",
          "Action" : [
            "ec2:RebootInstances",
          ]
        }
      ]
    })
  }
}
