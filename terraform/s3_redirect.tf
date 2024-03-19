locals {
  buckets = [
    data.aws_route53_zone.this.name,
    "www.${data.aws_route53_zone.this.name}",
  ]
}

resource "aws_s3_bucket" "redirect" {
  count = length(local.buckets)

  bucket = local.buckets[count.index]
}

resource "aws_s3_bucket_website_configuration" "redirect" {
  count = length(local.buckets)

  bucket = aws_s3_bucket.redirect[count.index].id

  redirect_all_requests_to {
    host_name = module.django.fqdn
    protocol  = "http"
  }
}

resource "aws_route53_record" "redirect" {
  count = length(local.buckets)

  zone_id = data.aws_route53_zone.this.zone_id
  name    = local.buckets[count.index]
  type    = "A"

  alias {
    name = aws_s3_bucket_website_configuration.redirect[count.index].website_endpoint
    # From https://docs.aws.amazon.com/general/latest/gr/s3.html#s3_website_region_endpoints
    zone_id                = "Z3AQBSTGFYJSTF"
    evaluate_target_health = false
  }
}
