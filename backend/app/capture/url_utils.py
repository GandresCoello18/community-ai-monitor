"""Utilities for camera stream URLs (FASE 11 — RTSP)."""

import re
from urllib.parse import urlparse, urlunparse

_IP_WEBCAM_RTSP = re.compile(
    r"^rtsp://(?P<host>[^/:]+)(?::8080)?/h264_(?:pcm|ulaw)\.sdp$",
    re.IGNORECASE,
)


def mask_stream_url(url: str | None) -> str | None:
    """Hide credentials in RTSP URLs for logs and API responses."""
    if not url:
        return url

    lowered = url.lower()
    if not lowered.startswith(("rtsp://", "rtsps://")):
        return url

    parsed = urlparse(url)
    if not parsed.username and not parsed.password:
        return url

    host = parsed.hostname or ""
    port_suffix = f":{parsed.port}" if parsed.port else ""
    safe_netloc = f"***@{host}{port_suffix}"
    safe = parsed._replace(netloc=safe_netloc)
    return urlunparse(safe)


def apply_rtsp_transport(url: str, transport: str) -> str:
    """Append rtsp_transport query param when not already present."""
    if "rtsp_transport=" in url.lower():
        return url
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}rtsp_transport={transport}"


def build_rtsp_ffmpeg_options(transport: str) -> str:
    """OpenCV-FFMPEG capture options for low-latency RTSP (IP Webcam, etc.)."""
    return (
        f"rtsp_transport;{transport}|"
        "fflags;nobuffer|"
        "max_delay;500000|"
        "stimeout;10000000"
    )


def is_ip_webcam_rtsp(url: str) -> bool:
    """True for IP Webcam mobile app RTSP endpoints (port 8080, h264_*.sdp)."""
    return _IP_WEBCAM_RTSP.match(url.strip()) is not None


def ip_webcam_http_url(rtsp_url: str) -> str | None:
    """Map IP Webcam RTSP URL to its MJPEG HTTP endpoint (/video)."""
    match = _IP_WEBCAM_RTSP.match(rtsp_url.strip())
    if match is None:
        return None
    host = match.group("host")
    return f"http://{host}:8080/video"
