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
  default     = "t2.micro"
}

variable "git_repository" {
  type        = string
  description = "The HTTP URL of the git repository to clone."
  sensitive   = true
}
