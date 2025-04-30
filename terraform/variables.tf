variable "heroku_api_key" {
  type        = string
  description = "The API key for the Heroku account."
  sensitive   = true
}

variable "google_oauth_client_id" {
  type        = string
  description = "The client ID of the Google OAuth2 application."
}

variable "google_oauth_secret" {
  type        = string
  sensitive   = true
  description = "The secret of the Google OAuth2 application."
}

variable "ec2_worker_ssh_public_key" {
  type        = string
  description = "An SSH public key to install on the EC2 worker."
}

variable "ec2_worker_instance_type" {
  type        = string
  description = "The instance type to use for the EC2 worker."
  default     = "g4dn.xlarge"
}

variable "git_repository" {
  type        = string
  description = "The SSH URL of the git repository to clone."
}

variable "django_sentry_dsn" {
  type        = string
  description = "The Sentry DSN for the Python Django application."
  sensitive   = true
}

variable "viewer_sentry_dsn" {
  type        = string
  description = "The Sentry DSN for the VolView Vue.js application."
  sensitive   = true
}

variable "redirect_url" {
  type        = string
  default     = null
  description = "If supplied, the Heroku app URL will redirect to whatever this URL is instead of the Heroku web dyno."
}
