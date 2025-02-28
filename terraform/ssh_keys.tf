resource "tls_private_key" "deploy_key" {
  algorithm = "ED25519"
}

resource "aws_secretsmanager_secret" "public_deploy_key" {
  name        = "github-deploy-public-key"
  description = "Public SSH key for cloning GitHub repo for deployment."
}

resource "aws_secretsmanager_secret_version" "deploy_key" {
  secret_id     = aws_secretsmanager_secret.public_deploy_key.id
  secret_string = tls_private_key.deploy_key.public_key_openssh
}

resource "aws_secretsmanager_secret" "private_deploy_key" {
  name        = "github-deploy-private-key"
  description = "Private SSH key for cloning GitHub repo for deployment."
}

resource "aws_secretsmanager_secret_version" "private_deploy_key" {
  secret_id     = aws_secretsmanager_secret.private_deploy_key.id
  secret_string = tls_private_key.deploy_key.private_key_openssh
}
