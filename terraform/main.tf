terraform {
  required_version = ">= 1.1"

  backend "remote" {
    organization = "kitware"

    workspaces {
      name = "xray-genius"
    }
  }

  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
    heroku = {
      source = "heroku/heroku"
    }
  }
}

provider "aws" {
  region = "us-east-1"
  # Must set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY envvars
}
provider "heroku" {
  api_key = var.heroku_api_key
}

data "aws_region" "current" {}
