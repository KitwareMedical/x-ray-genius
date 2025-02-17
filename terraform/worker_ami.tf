locals {
  celery_service_location  = "/etc/systemd/system/celery.service"
  celery_logfile_directory = "/var/log/celery"
  celery_logfile_filename  = "celery.log"
  django_project_location  = "/home/celery/xray-genius"
}

locals {
  environment_file_location = "${local.django_project_location}/.env"
}

resource "aws_iam_instance_profile" "image_builder" {
  name = "xray-genius-worker-ami-profile"
  role = aws_iam_role.image_builder.name
}

resource "aws_iam_role" "image_builder" {
  name = "xray-genius-worker-ami-role"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Action" : "sts:AssumeRole",
        "Principal" : {
          "Service" : "ec2.amazonaws.com"
        },
        "Effect" : "Allow",
        "Sid" : ""
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "role-policy-attachment" {
  for_each = toset([
    "arn:aws:iam::aws:policy/EC2InstanceProfileForImageBuilder",
    "arn:aws:iam::aws:policy/EC2InstanceProfileForImageBuilderECRContainerBuilds",
    "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
  ])

  role       = aws_iam_role.image_builder.name
  policy_arn = each.value
}

resource "aws_iam_role_policy" "image_builder" {
  name = "xray-genius-worker-ami-policy"
  role = aws_iam_role.image_builder.name
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Action" : "s3:GetObject",
        "Effect" : "Allow",
        "Resource" : "${aws_s3_bucket.image_builder.arn}/*"
      }
    ]
  })
}

data "aws_ami" "ec2_worker_launch_default" {
  owners      = ["099720109477"] # Canonical
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

resource "aws_imagebuilder_component" "image_builder" {
  name     = "deploy_xray_genius_worker"
  platform = "Linux"
  version  = "1.0.0"
  data = yamlencode({
    schemaVersion = 1.0
    phases = [{
      name = "build"
      steps = [
        {
          name      = "DownloadCeleryServiceAndConf"
          onFailure = "Abort"
          action    = "S3Download"
          inputs = [
            {
              source      = "s3://${aws_s3_bucket.image_builder.id}/${aws_s3_object.celery_service.key}"
              destination = local.celery_service_location
            }
          ]
        },
        {
          name      = "ConfigureCeleryService"
          onFailure = "Abort"
          action    = "ExecuteBash"
          inputs = {
            commands = [
              "sudo apt-get update",
              "sudo apt-get --yes upgrade",
              # Install AWS CloudWatch Logs agent
              "sudo apt-get --yes install collectd",
              "wget https://s3.amazonaws.com/amazoncloudwatch-agent/debian/amd64/latest/amazon-cloudwatch-agent.deb",
              "sudo dpkg --install --skip-same-version ./amazon-cloudwatch-agent.deb",
              "/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c ssm:${aws_ssm_parameter.celery_worker_cloudwatch_agent_config.name} -s",
              # Install Python
              "sudo add-apt-repository ppa:deadsnakes/ppa --yes",
              "sudo apt-get --yes install python3.12 python3.12-dev python3.12-venv",
              # Install Git
              "sudo apt-get --yes install git",
              # Install Heroku CLI
              "sudo curl https://cli-assets.heroku.com/install.sh | sh",
              # Install psycopg2 dependencies
              "sudo apt-get --yes install gcc g++ libpq-dev",
              "export PATH=/usr/lib/postgresql/X.Y/bin/:$PATH",
              # Install nvidia drivers + CUDA
              "sudo apt-get --yes install ubuntu-drivers-common",
              "sudo ubuntu-drivers install",
              "sudo apt-get --yes install nvidia-cuda-toolkit nvidia-cuda-dev",
              # Create celery user/group for systemd service
              "sudo useradd celery",
              "sudo mkdir /home/celery",
              # Go to home directory
              "pushd /home/celery",
              # Clone the xray-genius repository
              "git clone ${var.git_repository} ${local.django_project_location}",
              "pushd ${local.django_project_location}",
              # Create and activate a virtual environment
              "python3.12 -m venv venv",
              "source venv/bin/activate",
              # Install python dependencies
              "venv/bin/pip install --upgrade pip",
              "venv/bin/pip install -r requirements.worker.txt",
              # Ensure celery log directory exists
              "sudo mkdir -p ${local.celery_logfile_directory}",
              # Give `celery` user ownership of the home directory + log/run directories
              "sudo chown -R celery:celery /home/celery ${local.celery_logfile_directory}",
              # Enable the celery systemd service
              "sudo systemctl enable celery.service",
            ]
          }
      }]
    }]
  })
}

resource "aws_imagebuilder_image_recipe" "image_builder" {
  name         = "xray-genius-worker"
  parent_image = data.aws_ami.ec2_worker_launch_default.id
  version      = "1.0.0"

  component {
    component_arn = aws_imagebuilder_component.image_builder.arn
  }

  block_device_mapping {
    # The root volume, confirmed with `aws ec2 describe-images` command
    device_name = "/dev/sda1"
    ebs {
      delete_on_termination = true
      volume_size           = 100
      volume_type           = "gp3"
    }
  }
}

resource "aws_imagebuilder_infrastructure_configuration" "image_builder" {
  name                          = "xray-genius-worker"
  description                   = "EC2 image builder config for xray-genius celery worker"
  instance_profile_name         = aws_iam_instance_profile.image_builder.name
  instance_types                = [var.ec2_worker_instance_type]
  terminate_instance_on_failure = true
}

resource "aws_imagebuilder_image" "image_builder" {
  image_recipe_arn                 = aws_imagebuilder_image_recipe.image_builder.arn
  infrastructure_configuration_arn = aws_imagebuilder_infrastructure_configuration.image_builder.arn

  timeouts {
    create = "2h"
  }
}

resource "aws_s3_bucket" "image_builder" {
  bucket = "xray-genius-image-builder"
}

resource "aws_s3_object" "celery_service" {
  bucket  = aws_s3_bucket.image_builder.id
  key     = "celery.service"
  content = <<EOF
[Unit]
Description=Celery Service
After=network.target

[Service]
User=celery
Group=celery

WorkingDirectory=/home/celery/xray-genius/
RuntimeDirectory=celery

Environment=LC_ALL=C.UTF-8
Environment=LANG=C.UTF-8

# Application config environment
# Note, the '-' prefix in the EnvironmentFile directive indicates that the
# file may not exist at the time the service is started. This is needed
# because we create the EnvironmentFile in the ExecStartPre script.
EnvironmentFile=-${local.environment_file_location}

ExecStartPre=bash -c "export HEROKU_API_KEY='${var.heroku_api_key}' && git pull origin main && source ${local.django_project_location}/venv/bin/activate && pip install --upgrade pip && pip install -r requirements.worker.txt && heroku config --shell --app ${local.heroku_app_name} > ${local.environment_file_location}"
ExecStart=/home/celery/xray-genius/venv/bin/celery \
    --app xray_genius.celery \
    worker \
    --logfile ${local.celery_logfile_directory}/${local.celery_logfile_filename} \
    --loglevel INFO \
    --beat

TimeoutStopSec=90s
# Only SIGTERM the main process, since Celery is pre-fork by default
KillMode=mixed

Restart=always

[Install]
WantedBy=multi-user.target
EOF
}
