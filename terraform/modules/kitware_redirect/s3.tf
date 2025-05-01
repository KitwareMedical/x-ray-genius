data "aws_route53_zone" "this" {
  name = var.route53_hosted_zone
}

resource "aws_s3_bucket" "this" {
  bucket = var.fqdn
}

resource "aws_s3_bucket_website_configuration" "this" {
  bucket = aws_s3_bucket.this.id

  redirect_all_requests_to {
    host_name = var.redirect_url
  }
}

resource "aws_route53_record" "this" {
  zone_id = data.aws_route53_zone.this.zone_id
  name    = var.fqdn
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.this.domain_name
    zone_id                = aws_cloudfront_distribution.this.hosted_zone_id
    evaluate_target_health = false
  }
}
