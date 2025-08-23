from django.utils.timezone import now
from utils.models import LiveRecord
from ipware import get_client_ip

class LiveTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip, _ = get_client_ip(request)
        path = request.path
        referrer = request.META.get("HTTP_REFERER", "")
        user_agent = request.META.get("HTTP_USER_AGENT", "")

        record, created = LiveRecord.objects.get_or_create(
            ip_address=ip,
            defaults={
                "path": path,
                "referrer": referrer,
                "user_agent": user_agent,
            },
        )

        if not created:
            record.hit_count += 1
            record.path = path
            record.referrer = referrer
            record.user_agent = user_agent
            record.last_seen = now()
            record.save()

        return self.get_response(request)
