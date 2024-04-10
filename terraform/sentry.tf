data "sentry_organization" "this" {
  slug = "kitware-data"
}

resource "sentry_team" "this" {
  organization = data.sentry_organization.this.id

  name = "xray-genius"
  slug = "xray-genius"
}

resource "sentry_project" "django" {
  organization = data.sentry_organization.this.id

  teams = [sentry_team.this.id]
  name  = "xray-genius"
  slug  = "xray-genius"

  platform = "python-django"

  default_key   = true
  default_rules = true
}

data "sentry_key" "django" {
  organization = data.sentry_organization.this.id
  project      = sentry_project.django.id
}
