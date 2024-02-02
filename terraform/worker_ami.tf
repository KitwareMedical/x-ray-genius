locals {
  celery_service_location = "/etc/systemd/system/celery.service"
  celery_conf_location    = "/etc/conf.d/celery"
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
            },
            {
              source      = "s3://${aws_s3_bucket.image_builder.id}/${aws_s3_object.celery_conf.key}"
              destination = local.celery_conf_location
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
              # Install Python
              "sudo add-apt-repository ppa:deadsnakes/ppa --yes",
              "sudo apt-get --yes install python3.11 python3.11-dev python3.11-venv",
              # Install Git
              "sudo apt-get --yes install git",
              # Install psycopg2 dependencies
              "sudo apt-get --yes install gcc g++ libpq-dev",
              "export PATH=/usr/lib/postgresql/X.Y/bin/:$PATH",
              # Install nvidia drivers
              "sudo apt-get --yes install nvidia-headless-no-dkms-535 nvidia-cuda-dev",
              # Create celery user/group for systemd service
              "sudo useradd celery",
              "sudo mkdir /home/celery",
              # Go to home directory
              "pushd /home/celery",
              # Clone the xray-genius repository
              "git clone ${var.git_repository} xray-genius",
              "pushd xray-genius",
              # Create and activate a virtual environment
              "python3.11 -m venv venv",
              "source venv/bin/activate",
              # Ensure celery log/run directories exists
              "sudo mkdir -p /var/log/celery /var/run/celery",
              # Give `celery` user ownership of the home directory + log/run directories
              "sudo chown -R celery:celery /home/celery /var/log/celery /var/run/celery",
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
      volume_size           = 40
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
Type=forking
User=celery
Group=celery
EnvironmentFile=${local.celery_conf_location}
WorkingDirectory=/home/celery/xray-genius/
RuntimeDirectory=celery
ExecStartPre=bash -c "git pull origin main && source venv/bin/activate && pip install --upgrade pip && pip install .[worker]"
ExecStart=bash -c "$${CELERY_BIN} -A $${CELERY_APP} multi start $${CELERYD_NODES} \
    --pidfile=$${CELERYD_PID_FILE} --logfile=$${CELERYD_LOG_FILE} \
    --loglevel=$${CELERYD_LOG_LEVEL} $${CELERYD_OPTS}"
ExecStop=bash -c "$${CELERY_BIN} multi stopwait $${CELERYD_NODES} \
    --pidfile=$${CELERYD_PID_FILE} --logfile=$${CELERYD_LOG_FILE} \
    --loglevel=$${CELERYD_LOG_LEVEL}"
ExecReload=bash -c "$${CELERY_BIN} -A $${CELERY_APP} multi restart $${CELERYD_NODES} \
    --pidfile=$${CELERYD_PID_FILE} --logfile=$${CELERYD_LOG_FILE} \
    --loglevel=$${CELERYD_LOG_LEVEL} $${CELERYD_OPTS}"
Restart=always

[Install]
WantedBy=multi-user.target
EOF
}

resource "aws_s3_object" "celery_conf" {
  bucket = aws_s3_bucket.image_builder.id
  key    = "celery.conf"
  content = <<EOF
# See
# https://docs.celeryq.dev/en/latest/userguide/daemonizing.html#usage-systemd

CELERY_APP="xray_genius.celery"
CELERYD_NODES="worker"
CELERYD_OPTS=""
CELERY_BIN="/home/celery/xray-genius/venv/bin/celery"
CELERYD_PID_FILE="/var/run/celery/%n.pid"
CELERYD_LOG_FILE="/var/log/celery/%n%I.log"
CELERYD_LOG_LEVEL="INFO"

# The below lines should be uncommented if using the celerybeat.service example
# unit file, but are unnecessary otherwise
# CELERYBEAT_PID_FILE="/var/run/celery/beat.pid"
# CELERYBEAT_LOG_FILE="/var/log/celery/beat.log"

# Django environment variables
${join("\n", [
  for k, v in module.django.all_django_vars : "${k}=\"${v}\""
])}
EOF
}
