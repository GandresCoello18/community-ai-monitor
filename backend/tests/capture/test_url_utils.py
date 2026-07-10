from app.capture.url_utils import apply_rtsp_transport, build_rtsp_ffmpeg_options, mask_stream_url


def test_mask_stream_url_hides_credentials() -> None:
    url = "rtsp://admin:secret123@192.168.1.50:554/stream1"
    masked = mask_stream_url(url)

    assert "secret123" not in masked
    assert "admin" not in masked
    assert "192.168.1.50" in masked
    assert masked.startswith("rtsp://***@")


def test_mask_stream_url_without_credentials_unchanged() -> None:
    url = "rtsp://192.168.1.50:554/stream1"
    assert mask_stream_url(url) == url


def test_mask_stream_url_non_rtsp_unchanged() -> None:
    assert mask_stream_url("webcam://0") == "webcam://0"


def test_apply_rtsp_transport_appends_param() -> None:
    url = "rtsp://192.168.1.50/stream1"
    result = apply_rtsp_transport(url, "tcp")

    assert "rtsp_transport=tcp" in result


def test_apply_rtsp_transport_skips_if_present() -> None:
    url = "rtsp://192.168.1.50/stream1?rtsp_transport=udp"
    assert apply_rtsp_transport(url, "tcp") == url


def test_build_rtsp_ffmpeg_options_includes_transport() -> None:
    options = build_rtsp_ffmpeg_options("udp")
    assert "rtsp_transport;udp" in options
    assert "fflags;nobuffer" in options
