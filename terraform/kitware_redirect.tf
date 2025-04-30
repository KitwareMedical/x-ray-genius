module "kitware_redirect" {
  count = var.redirect_url != null ? 1 : 0

  source = "./modules/kitware_redirect"

  fqdn                = module.django.fqdn
  route53_hosted_zone = data.aws_route53_zone.this.name
  redirect_url        = var.redirect_url
}
