variable "google_oauth_client_id" {
  type        = string
  description = "The client ID of the Google OAuth2 application."
}

variable "google_oauth_secret" {
  type        = string
  sensitive   = true
  description = "The secret of the Google OAuth2 application."
}
