locals {
  lambda_runtime = "python3.12"
}

resource "aws_iam_role" "restart_worker_lambda" {
  name = "xray-genius-restart-worker-lambda-role"

  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",

        "Principal" : {
          "Service" : "lambda.amazonaws.com"
        },
        "Action" : "sts:AssumeRole",
      }
    ]
  })
}

data "aws_iam_policy" "lambda_policy" {
  arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "restart_worker_lambda" {
  role       = aws_iam_role.restart_worker_lambda.name
  policy_arn = data.aws_iam_policy.lambda_policy.arn
}

resource "aws_iam_policy" "lambda_policy_ec2" {
  name = "xray-genius-restart-worker-lambda-policy"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "RebootEC2Worker",
        "Effect" : "Allow",
        "Resource" : "*",
        "Action" : [
          "ec2:DescribeInstances",
          "ec2:RebootInstances",
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy_ec2" {
  role       = aws_iam_role.restart_worker_lambda.name
  policy_arn = aws_iam_policy.lambda_policy_ec2.arn
}

data "archive_file" "restart_worker_lambda_code" {
  type        = "zip"
  source_dir  = "${path.module}/worker_restarter/"
  output_path = "${path.module}/worker_restarter.zip"

  depends_on = [null_resource.restart_worker_lambda_pip_install]
}

resource "null_resource" "restart_worker_lambda_pip_install" {
  triggers = {
    shell_hash = "${sha256(file("${path.module}/worker_restarter/requirements.txt"))}/${sha256(file("${path.module}/worker_restarter/restart.py"))}"
  }

  provisioner "local-exec" {
    command = "python3 -m pip install -r worker_restarter/requirements.txt -t ${path.module}/worker_restarter"
  }
}

resource "aws_lambda_function" "restart_worker_lambda" {
  filename         = data.archive_file.restart_worker_lambda_code.output_path
  source_code_hash = data.archive_file.restart_worker_lambda_code.output_base64sha256

  function_name = "restart_worker"
  handler       = "restart.handler"
  runtime       = local.lambda_runtime
  role          = aws_iam_role.restart_worker_lambda.arn
  timeout       = 10

  environment {
    variables = {
      SENTRY_DSN = var.django_sentry_dsn
    }
  }

  reserved_concurrent_executions = 1
}

resource "aws_lambda_function_url" "restart_worker_lambda" {
  function_name      = aws_lambda_function.restart_worker_lambda.id
  authorization_type = "NONE"
}

resource "heroku_app_webhook" "restart_worker_lambda" {
  app_id = module.django.heroku_app_id
  level  = "sync"
  url    = aws_lambda_function_url.restart_worker_lambda.function_url

  # See https://devcenter.heroku.com/articles/app-webhooks#step-2-determine-which-events-to-subscribe-to
  include = [
    "api:release",          # A new release for the app has been initiated or the release’s status has changed since the last notification.
  ]
}
