data "aws_route53_zone" "this" {
  # This must be created by hand in the AWS console
  name = "xray-genius.com"
}

data "heroku_team" "this" {
  name = "kitware"
}

locals {
  heroku_app_name = "otm-xray-genius"
}

module "django" {
  source  = "kitware-resonant/resonant/heroku"
  version = "1.1.1"

  project_slug     = "xray-genius"
  route53_zone_id  = data.aws_route53_zone.this.zone_id
  heroku_app_name  = local.heroku_app_name
  heroku_team_name = data.heroku_team.this.name
  subdomain_name   = "app"

  # We're using EC2 workers instead.
  heroku_worker_dyno_quantity = 0

  heroku_postgresql_plan = "essential-0"

  ec2_worker_instance_quantity = 1
  ec2_worker_instance_type     = var.ec2_worker_instance_type
  ec2_worker_launch_ami_id     = tolist(aws_imagebuilder_image.image_builder.output_resources[0].amis)[0].image
  ec2_worker_ssh_public_key    = var.ec2_worker_ssh_public_key
  ec2_worker_volume_size       = 100 # deepdrr requires more disk space than the default 30 GB.

  additional_django_vars = {
    DJANGO_ADDITIONAL_ADMIN_EMAILS = "kitware@kitware.com"
    DJANGO_GOOGLE_OAUTH_CLIENT_ID  = var.google_oauth_client_id
    DJANGO_GOOGLE_OAUTH_SECRET     = var.google_oauth_secret
    DJANGO_SENTRY_DSN              = var.django_sentry_dsn
    VITE_SENTRY_DSN                = var.viewer_sentry_dsn
  }

  # This is needed in order to run the node build process for
  # the Django server-rendered templates
  heroku_additional_buildpacks = [
    "https://github.com/dmathieu/heroku-buildpack-submodules.git",
    "heroku/nodejs",
  ]

  # Disable cloudamqp, use Redis as celery broker instead
  heroku_cloudamqp_plan = null
}

resource "heroku_addon" "heroku_redis" {
  count  = 1
  app_id = module.django.heroku_app_id
  plan   = "heroku-redis:mini"
}
