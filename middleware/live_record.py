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

        record = LiveRecord.objects.filter(ip_address=ip).first()
        if record:
            record.hit_count += 1
            record.path = path
            record.referrer = referrer
            record.user_agent = user_agent
            record.last_seen = now()
            record.save()
        else:
            record = LiveRecord.objects.create(
                ip_address=ip,
                path=path,
                referrer=referrer,
                user_agent=user_agent,
            )

        return self.get_response(request)
