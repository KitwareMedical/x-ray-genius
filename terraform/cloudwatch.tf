resource "aws_cloudwatch_log_group" "celery_worker_cloudwatch_agent_config" {
  name = "xray-genius-worker-celery-logs"
}

resource "aws_iam_role_policy_attachment" "celery_worker_cloudwatch_agent_config" {
  for_each = toset([
    "arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforSSM",
    "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
  ])

  role       = module.django.ec2_worker_iam_role_id
  policy_arn = each.value
}

data "template_file" "celery_worker_cloudwatch_agent_config" {
  template = file("${path.module}/cloudwatch_agent_config.json.tpl")

  vars = {
    log_group_name = aws_cloudwatch_log_group.celery_worker_cloudwatch_agent_config.name
    log_file_path  = "${local.celery_logfile_directory}/${local.celery_logfile_filename}"
  }
}

resource "aws_ssm_parameter" "celery_worker_cloudwatch_agent_config" {
  name  = "xray-genius-worker-cloudwatch-agent-config"
  type  = "String"
  value = data.template_file.celery_worker_cloudwatch_agent_config.rendered
}
