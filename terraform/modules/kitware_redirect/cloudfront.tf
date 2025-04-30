locals {
  origin_id = "origin-${var.fqdn}"
}

data "aws_cloudfront_cache_policy" "this" {
  name = "Managed-CachingDisabled"
}

resource "aws_cloudfront_distribution" "this" {
  http_version = "http2"

  origin {
    origin_id   = local.origin_id
    domain_name = aws_s3_bucket_website_configuration.this.website_endpoint

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  enabled = true

  price_class = "PriceClass_100"

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    cache_policy_id        = data.aws_cloudfront_cache_policy.this.id #"4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
    target_origin_id       = local.origin_id
    viewer_protocol_policy = "allow-all"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate.cert.arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1"
  }

  aliases = [var.fqdn]
}
