"""Utilities for camera stream URLs (FASE 11 — RTSP)."""

from urllib.parse import urlparse, urlunparse


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
        "flags;low_delay|"
        "max_delay;500000|"
        "stimeout;10000000"
    )
