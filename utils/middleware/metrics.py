# yourapp/middleware/metrics.py
import time
import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from utils.utils import client_ip

security_logger = logging.getLogger("security")

SUSPICIOUS_PATHS = ("/wp-login.php", "/.env", "/admin/login.php", "/phpmyadmin")

class MetricsMiddleware:
    """
    - measures latency
    - counts status classes (2xx/3xx/4xx/5xx)
    - emits suspicious event if path matches known scans
    - pushes snapshots to WS group "metrics"
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

        # push a compact metric
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
            pass  # don’t block the request path

        # suspicious paths
        if any(request.path.startswith(p) for p in SUSPICIOUS_PATHS):
            ip = client_ip(request)
            note = f"suspicious path hit: {request.path}"
            security_logger.warning(note, extra={"request_id": getattr(request, "request_id", "-")})
            # fire WS
            try:
                async_to_sync(self.channel_layer.group_send)(
                    "security", {"type": "security.message", "payload": {
                        "ip": ip, "path": request.path, "method": request.method,
                        "note": note, "severity": "med"
                    }}
                )
            except Exception:
                pass

        return response
