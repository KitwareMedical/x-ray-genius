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

moved {
  from = sentry_project.this
  to   = sentry_project.django
}

data "sentry_key" "django" {
  organization = data.sentry_organization.this.id
  project      = sentry_project.django.id
}

resource "sentry_project" "viewer" {
  organization = data.sentry_organization.this.id

  teams = [sentry_team.this.id]
  name  = "xray-genius-viewer"
  slug  = "xray-genius-viewer"

  platform = "javascript-vue"

  default_key   = true
  default_rules = true
}

data "sentry_key" "viewer" {
  organization = data.sentry_organization.this.id
  project      = sentry_project.viewer.id
}
