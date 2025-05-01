resource "aws_acm_certificate" "cert" {
  domain_name       = var.fqdn
  validation_method = "DNS"
}

locals {
  certificate_validation_options = tolist(aws_acm_certificate.cert.domain_validation_options)[0]
}

resource "aws_route53_record" "cert_validation" {
  allow_overwrite = true

  ttl     = 60
  name    = local.certificate_validation_options.resource_record_name
  records = [local.certificate_validation_options.resource_record_value]
  type    = local.certificate_validation_options.resource_record_type

  zone_id = data.aws_route53_zone.this.zone_id
}

resource "aws_acm_certificate_validation" "cert" {
  certificate_arn         = aws_acm_certificate.cert.arn
  validation_record_fqdns = [aws_route53_record.cert_validation.fqdn]
}
