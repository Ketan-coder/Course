import time
import logging
import json
from django.utils.timezone import now
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from utils.utils import client_ip
from utils.models import LiveRecord  # adjust import to where your model lives

security_logger = logging.getLogger("security")

SUSPICIOUS_PATHS = ("/wp-login.php", "/.env", "/admin/login.php", "/phpmyadmin")


class MetricsMiddleware:
    """
    - measures latency
    - counts status classes (2xx/3xx/4xx/5xx)
    - emits suspicious event if path matches known scans
    - pushes snapshots to WS group "metrics"
    - records live visitor activity and pushes to WS group "records"
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.channel_layer = get_channel_layer()

    def __call__(self, request):
        start = time.perf_counter()
        response = self.get_response(request)
        latency_ms = int((time.perf_counter() - start) * 1000)

        status = response.status_code
        status_bucket = f"{status//100}xx"

        # --- METRICS PUSH ---
        payload = {
            "type": "metric.update",
            "latency_ms": latency_ms,
            "status_bucket": status_bucket,
            "path": request.path[:120],
            "ts": int(time.time()),
        }
        try:
            async_to_sync(self.channel_layer.group_send)(
                "metrics", {"type": "metrics.message", "payload": payload}
            )
        except Exception:
            pass

        # --- SUSPICIOUS PATH DETECTION ---
        if any(request.path.startswith(p) for p in SUSPICIOUS_PATHS):
            ip = client_ip(request)
            note = f"suspicious path hit: {request.path}"
            security_logger.warning(note, extra={"req_id": getattr(request, "request_id", "-")})
            try:
                async_to_sync(self.channel_layer.group_send)(
                    "security",
                    {
                        "type": "security.message",
                        "payload": {
                            "ip": ip,
                            "path": request.path,
                            "method": request.method,
                            "note": note,
                            "severity": "med",
                        },
                    },
                )
            except Exception:
                pass

        # --- RECORD LIVE VISITOR ---
        try:
            ip = client_ip(request)
            ua = request.META.get("HTTP_USER_AGENT", "-")
            ref = request.META.get("HTTP_REFERER", "-")

            # update or create record for this IP + path
            record = (
                LiveRecord.objects.filter(
                    ip_address=ip,
                    path=request.path[:255],
                    status="active"
                ).order_by("-last_seen").first()
            )

            if record:
                record.hit_count += 1
                record.last_seen = now()
                record.save(update_fields=["hit_count", "last_seen"])
            else:
                record = LiveRecord.objects.create(
                    ip_address=ip,
                    path=request.path,
                    referrer=ref,
                    user_agent=ua,
                    status="active",
                )

            # push over websocket
            record_payload = {
                "ip": record.ip_address,
                "path": record.path,
                "referrer": record.referrer,
                "user_agent": record.user_agent[:100],  # don’t spam with huge UA
                "hit_count": record.hit_count,
                "first_seen": record.first_seen.isoformat(),
                "last_seen": record.last_seen.isoformat(),
                "status": record.status,
            }
            async_to_sync(self.channel_layer.group_send)(
                "records", {"type": "records.message", "payload": record_payload}
            )

        except Exception as e:
            logging.error(f"LiveRecord update failed: {e}", exc_info=True)

        return response
