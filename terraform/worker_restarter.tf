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

resource "random_password" "lambda_secret" {
  length  = 64
  special = true
}

data "archive_file" "restart_worker_lambda_code" {
  type        = "zip"
  source_dir  = "${path.module}/worker_restarter/"
  output_path = "${path.module}/worker_restarter.zip"

  depends_on = [null_resource.restart_worker_lambda_pip_install]
}

resource "null_resource" "restart_worker_lambda_pip_install" {
  triggers = {
    # Ensure this resource is recreated if the requirements.txt or restart.py files change
    shell_hash = filesha1("${path.module}/worker_restarter/requirements.txt")
  }

  provisioner "local-exec" {
    command = <<EOT
      set -e
      mkdir -p ${path.module}/worker_restarter_packages/python/
      python3 -m pip install -r ${path.module}/worker_restarter/requirements.txt -t ${path.module}/worker_restarter_packages/python/
    EOT
  }
}

data "archive_file" "restart_worker_lambda_dependencies" {
  type        = "zip"
  source_dir  = "${path.module}/worker_restarter_packages"
  output_path = "${path.module}/layer.zip"

  depends_on = [null_resource.restart_worker_lambda_pip_install]
}

resource "aws_s3_object" "lambda_layer_zip" {
  bucket     = aws_s3_bucket.image_builder.id
  key        = "lambda_layers/worker_restarter.zip"
  source     = data.archive_file.restart_worker_lambda_dependencies.output_path
  depends_on = [null_resource.restart_worker_lambda_pip_install]
}

resource "aws_lambda_layer_version" "restart_worker_lambda" {
  layer_name          = "worker_restarter_dependencies"
  s3_bucket           = aws_s3_bucket.image_builder.bucket
  s3_key              = aws_s3_object.lambda_layer_zip.key
  compatible_runtimes = [local.lambda_runtime]
  depends_on          = [aws_s3_object.lambda_layer_zip]
}

resource "aws_lambda_function" "restart_worker_lambda" {
  filename         = data.archive_file.restart_worker_lambda_code.output_path
  source_code_hash = data.archive_file.restart_worker_lambda_code.output_base64sha256
  layers           = [aws_lambda_layer_version.restart_worker_lambda.arn]

  function_name = "restart_worker"
  handler       = "restart.handler"
  runtime       = local.lambda_runtime
  role          = aws_iam_role.restart_worker_lambda.arn
  timeout       = 10

  environment {
    variables = {
      SENTRY_DSN    = var.django_sentry_dsn
      WEBHOOK_TOKEN = random_password.lambda_secret.result
    }
  }

  reserved_concurrent_executions = 1

  # Ensure the Lambda function is recreated if the code or dependencies change
  depends_on = [null_resource.restart_worker_lambda_pip_install]
}

resource "aws_lambda_function_url" "restart_worker_lambda" {
  function_name      = aws_lambda_function.restart_worker_lambda.id
  authorization_type = "NONE"
}

resource "heroku_app_webhook" "restart_worker_lambda" {
  app_id        = module.django.heroku_app_id
  level         = "sync"
  url           = aws_lambda_function_url.restart_worker_lambda.function_url
  authorization = "Bearer ${random_password.lambda_secret.result}"

  # See https://devcenter.heroku.com/articles/app-webhooks#step-2-determine-which-events-to-subscribe-to
  include = [
    "api:release", # A new release for the app has been initiated or the release’s status has changed since the last notification.
  ]
}
