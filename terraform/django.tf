data "aws_route53_zone" "this" {
  # This must be created by hand in the AWS console
  name = "xray-genius.com"
}

data "heroku_team" "this" {
  name = "kitware"
}

module "django" {
  source  = "girder/girder4/heroku"
  version = "0.13.0"

  project_slug     = "xray-genius"
  route53_zone_id  = data.aws_route53_zone.this.zone_id
  heroku_team_name = data.heroku_team.this.name
  subdomain_name   = "www"

  # We're using EC2 workers instead.
  heroku_worker_dyno_quantity = 0

  ec2_worker_instance_quantity = 1
  ec2_worker_instance_type     = var.ec2_worker_instance_type
  ec2_worker_launch_ami_id     = tolist(aws_imagebuilder_image.image_builder.output_resources[0].amis)[0].image
  ec2_worker_ssh_public_key    = var.ec2_worker_ssh_public_key
  ec2_worker_volume_size       = 100 # deepdrr requires more disk space than the default 30 GB.

  additional_django_vars = {
    DJANGO_GOOGLE_OAUTH_CLIENT_ID = var.google_oauth_client_id
    DJANGO_GOOGLE_OAUTH_SECRET    = var.google_oauth_secret
    DJANGO_SENTRY_DSN             = data.sentry_key.this.dsn_public
  }

  # This is needed in order to run the node build process for
  # the Django server-rendered templates
  heroku_additional_buildpacks = [
    "https://github.com/dmathieu/heroku-buildpack-submodules.git",
    "heroku/nodejs",
  ]
}
