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
  }
}
