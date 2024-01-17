data "sentry_organization" "this" {
  slug = "kitware-data"
}

resource "sentry_team" "this" {
  organization = data.sentry_organization.this.id

  name = "xray-genius"
  slug = "xray-genius"
}

resource "sentry_project" "this" {
  organization = data.sentry_organization.this.id

  teams = [sentry_team.this.id]
  name  = "xray-genius"
  slug  = "xray-genius"

  platform = "python"
}

data "sentry_key" "this" {
  organization = data.sentry_organization.this.id
  project      = sentry_project.this.id
}
