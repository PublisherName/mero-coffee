data "aws_route53_zone" "main" {
  count = var.domain_name != "" ? 1 : 0
  name  = "${var.domain_name}."
}

data "aws_acm_certificate" "main" {
  count    = var.domain_name != "" ? 1 : 0
  domain   = var.domain_name
  statuses = ["ISSUED"]
}

resource "aws_route53_record" "app" {
  count   = var.domain_name != "" ? 1 : 0
  zone_id = data.aws_route53_zone.main[0].zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = aws_lb.mc_alb.dns_name
    zone_id                = aws_lb.mc_alb.zone_id
    evaluate_target_health = true
  }
}
