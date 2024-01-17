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

  additional_django_vars = {
    DJANGO_SENTRY_DSN = data.sentry_key.this.dsn_public
  }

  # This is needed in order to run the node build process for
  # the Django server-rendered templates
  heroku_additional_buildpacks = ["heroku/nodejs"]
}
