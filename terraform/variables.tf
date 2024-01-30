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
