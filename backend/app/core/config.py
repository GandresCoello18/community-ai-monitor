from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    app_name: str = "Community AI Monitor"
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    seed_demo_data: bool = Field(default=True, alias="SEED_DEMO_DATA")

    api_v1_prefix: str = "/api/v1"
    default_page_size: int = Field(default=20, alias="DEFAULT_PAGE_SIZE")
    max_page_size: int = Field(default=100, alias="MAX_PAGE_SIZE")

    database_url: str = Field(
        default="postgresql://cam_user:cam_dev_password@localhost:5432/community_ai_monitor",
        alias="DATABASE_URL",
    )

    camera_simulator_enabled: bool = Field(
        default=True,
        alias="CAMERA_SIMULATOR_ENABLED",
    )
    camera_simulator_auto_start: bool = Field(
        default=False,
        alias="CAMERA_SIMULATOR_AUTO_START",
    )
    camera_simulator_fps: float = Field(
        default=2.0,
        alias="CAMERA_SIMULATOR_FPS",
    )
    camera_simulator_video_path: str | None = Field(
        default=None,
        alias="CAMERA_SIMULATOR_VIDEO_PATH",
    )

    # --- Live preview (in-memory only, not persisted) ---
    camera_preview_enabled: bool = Field(
        default=True,
        alias="CAMERA_PREVIEW_ENABLED",
    )
    camera_preview_fps: float = Field(default=2.0, alias="CAMERA_PREVIEW_FPS")
    camera_preview_max_width: int = Field(
        default=640,
        alias="CAMERA_PREVIEW_MAX_WIDTH",
    )
    camera_preview_jpeg_quality: int = Field(
        default=75,
        alias="CAMERA_PREVIEW_JPEG_QUALITY",
    )
    camera_preview_show_detections: bool = Field(
        default=True,
        alias="CAMERA_PREVIEW_SHOW_DETECTIONS",
    )
    camera_worker_shutdown_timeout_seconds: float = Field(
        default=5.0,
        alias="CAMERA_WORKER_SHUTDOWN_TIMEOUT_SECONDS",
    )

    # --- Computer Vision (FASE 5) ---
    detection_enabled: bool = Field(default=True, alias="DETECTION_ENABLED")
    detection_model: str = Field(default="yolov8n.pt", alias="DETECTION_MODEL")
    detection_confidence: float = Field(default=0.4, alias="DETECTION_CONFIDENCE")
    detection_device: str = Field(default="cpu", alias="DETECTION_DEVICE")
    detection_classes: str = Field(
        default="person,bicycle,car,motorcycle,bus,truck,dog,cat",
        alias="DETECTION_CLASSES",
    )
    detection_interval_seconds: float = Field(
        default=1.0,
        alias="DETECTION_INTERVAL_SECONDS",
    )
    detection_persist_enabled: bool = Field(
        default=True,
        alias="DETECTION_PERSIST_ENABLED",
    )

    tracking_iou_threshold: float = Field(default=0.3, alias="TRACKING_IOU_THRESHOLD")
    tracking_max_age: int = Field(default=30, alias="TRACKING_MAX_AGE")

    # --- Event Engine (FASE 6) ---
    event_engine_enabled: bool = Field(default=True, alias="EVENT_ENGINE_ENABLED")
    event_persist_enabled: bool = Field(default=True, alias="EVENT_PERSIST_ENABLED")
    event_cooldown_seconds: float = Field(default=60.0, alias="EVENT_COOLDOWN_SECONDS")

    event_crowd_enabled: bool = Field(default=True, alias="EVENT_CROWD_ENABLED")
    event_crowd_people_threshold: int = Field(
        default=5,
        alias="EVENT_CROWD_PEOPLE_THRESHOLD",
    )

    event_high_density_enabled: bool = Field(
        default=True,
        alias="EVENT_HIGH_DENSITY_ENABLED",
    )
    event_high_density_min_people: int = Field(
        default=3,
        alias="EVENT_HIGH_DENSITY_MIN_PEOPLE",
    )
    event_high_density_threshold: float = Field(
        default=0.15,
        alias="EVENT_HIGH_DENSITY_THRESHOLD",
    )

    event_long_presence_enabled: bool = Field(
        default=True,
        alias="EVENT_LONG_PRESENCE_ENABLED",
    )
    event_long_presence_seconds: float = Field(
        default=30.0,
        alias="EVENT_LONG_PRESENCE_SECONDS",
    )
    event_long_presence_classes: str = Field(
        default="person",
        alias="EVENT_LONG_PRESENCE_CLASSES",
    )

    event_abandoned_object_enabled: bool = Field(
        default=True,
        alias="EVENT_ABANDONED_OBJECT_ENABLED",
    )
    event_abandoned_duration_seconds: float = Field(
        default=600.0,
        alias="EVENT_ABANDONED_DURATION_SECONDS",
    )
    event_abandoned_movement_threshold: float = Field(
        default=15.0,
        alias="EVENT_ABANDONED_MOVEMENT_THRESHOLD",
    )
    event_abandoned_classes: str = Field(
        default="backpack,handbag,suitcase",
        alias="EVENT_ABANDONED_CLASSES",
    )

    # --- Community Rule Engine ---
    rule_engine_enabled: bool = Field(default=True, alias="RULE_ENGINE_ENABLED")
    rule_scene_type: str = Field(default="general", alias="RULE_SCENE_TYPE")
    rule_emit_legacy_event_types: bool = Field(
        default=True,
        alias="RULE_EMIT_LEGACY_EVENT_TYPES",
    )
    rule_crowd_threshold: int = Field(default=15, alias="RULE_CROWD_THRESHOLD")
    rule_person_long_stay_enabled: bool = Field(
        default=True,
        alias="RULE_PERSON_LONG_STAY_ENABLED",
    )
    rule_person_long_stay_seconds: float = Field(
        default=1200.0,
        alias="RULE_PERSON_LONG_STAY_SECONDS",
    )
    rule_person_repeated_activity_enabled: bool = Field(
        default=True,
        alias="RULE_PERSON_REPEATED_ACTIVITY_ENABLED",
    )
    rule_person_repeated_activity_window_seconds: float = Field(
        default=1800.0,
        alias="RULE_PERSON_REPEATED_ACTIVITY_WINDOW_SECONDS",
    )
    rule_person_repeated_activity_min_visits: int = Field(
        default=3,
        alias="RULE_PERSON_REPEATED_ACTIVITY_MIN_VISITS",
    )
    rule_person_repeated_activity_zone_radius: float = Field(
        default=80.0,
        alias="RULE_PERSON_REPEATED_ACTIVITY_ZONE_RADIUS",
    )
    rule_person_hidden_activity_enabled: bool = Field(
        default=True,
        alias="RULE_PERSON_HIDDEN_ACTIVITY_ENABLED",
    )
    rule_person_hidden_stay_seconds: float = Field(
        default=900.0,
        alias="RULE_PERSON_HIDDEN_STAY_SECONDS",
    )
    rule_person_hidden_max_movement: float = Field(
        default=20.0,
        alias="RULE_PERSON_HIDDEN_MAX_MOVEMENT",
    )
    rule_vehicle_long_parking_enabled: bool = Field(
        default=True,
        alias="RULE_VEHICLE_LONG_PARKING_ENABLED",
    )
    rule_vehicle_parking_seconds: float = Field(
        default=600.0,
        alias="RULE_VEHICLE_PARKING_SECONDS",
    )
    rule_vehicle_parking_movement_threshold: float = Field(
        default=15.0,
        alias="RULE_VEHICLE_PARKING_MOVEMENT_THRESHOLD",
    )
    rule_double_parking_enabled: bool = Field(
        default=True,
        alias="RULE_DOUBLE_PARKING_ENABLED",
    )
    rule_double_parking_seconds: float = Field(
        default=180.0,
        alias="RULE_DOUBLE_PARKING_SECONDS",
    )
    rule_street_zone_y_start: float = Field(
        default=0.55,
        alias="RULE_STREET_ZONE_Y_START",
    )
    rule_wrong_direction_enabled: bool = Field(
        default=False,
        alias="RULE_WRONG_DIRECTION_ENABLED",
    )
    rule_expected_traffic_direction: str = Field(
        default="ltr",
        alias="RULE_EXPECTED_TRAFFIC_DIRECTION",
    )
    rule_wrong_direction_min_displacement: float = Field(
        default=40.0,
        alias="RULE_WRONG_DIRECTION_MIN_DISPLACEMENT",
    )
    rule_park_occupancy_enabled: bool = Field(
        default=True,
        alias="RULE_PARK_OCCUPANCY_ENABLED",
    )
    rule_park_occupancy_change_threshold: int = Field(
        default=5,
        alias="RULE_PARK_OCCUPANCY_CHANGE_THRESHOLD",
    )
    rule_park_empty_enabled: bool = Field(
        default=True,
        alias="RULE_PARK_EMPTY_ENABLED",
    )
    rule_park_empty_seconds: float = Field(
        default=1800.0,
        alias="RULE_PARK_EMPTY_SECONDS",
    )
    rule_abandoned_object_seconds: float = Field(
        default=900.0,
        alias="RULE_ABANDONED_OBJECT_SECONDS",
    )
    rule_animal_enabled: bool = Field(
        default=True,
        alias="RULE_ANIMAL_ENABLED",
    )
    rule_animal_classes: str = Field(
        default="dog,cat",
        alias="RULE_ANIMAL_CLASSES",
    )
    rule_animal_cooldown_seconds: float = Field(
        default=60.0,
        alias="RULE_ANIMAL_COOLDOWN_SECONDS",
    )
    rule_trash_detected_enabled: bool = Field(
        default=False,
        alias="RULE_TRASH_DETECTED_ENABLED",
    )
    rule_obstruction_detected_enabled: bool = Field(
        default=False,
        alias="RULE_OBSTRUCTION_DETECTED_ENABLED",
    )
    rule_metrics_enabled: bool = Field(default=True, alias="RULE_METRICS_ENABLED")

    # --- LLM (FASE 7) ---
    llm_provider: str = Field(default="ollama", alias="LLM_PROVIDER")
    llm_base_url: str = Field(
        default="http://localhost:11434",
        alias="LLM_BASE_URL",
    )
    llm_model: str = Field(default="llama3.2:3b", alias="LLM_MODEL")
    llm_timeout_seconds: float = Field(default=120.0, alias="LLM_TIMEOUT_SECONDS")
    llm_temperature: float = Field(default=0.3, alias="LLM_TEMPERATURE")
    summary_max_events: int = Field(default=200, alias="SUMMARY_MAX_EVENTS")

    # --- WebSocket (FASE 9) ---
    websocket_enabled: bool = Field(default=True, alias="WEBSOCKET_ENABLED")

    # --- Notifications (FASE 12) ---
    notifications_enabled: bool = Field(default=False, alias="NOTIFICATIONS_ENABLED")
    notification_provider: str = Field(default="telegram", alias="NOTIFICATION_PROVIDER")
    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str = Field(default="", alias="TELEGRAM_CHAT_ID")
    notify_min_severity: str = Field(default="medium", alias="NOTIFY_MIN_SEVERITY")
    notify_photo_min_severity: str = Field(
        default="high",
        alias="NOTIFY_PHOTO_MIN_SEVERITY",
    )
    notify_event_types: str = Field(default="", alias="NOTIFY_EVENT_TYPES")
    notify_cooldown_seconds: float = Field(
        default=300.0,
        alias="NOTIFY_COOLDOWN_SECONDS",
    )
    notify_quiet_hours_start: str = Field(
        default="",
        alias="NOTIFY_QUIET_HOURS_START",
    )
    notify_quiet_hours_end: str = Field(
        default="",
        alias="NOTIFY_QUIET_HOURS_END",
    )
    notify_alert_jpeg_max_width: int = Field(
        default=640,
        alias="NOTIFY_ALERT_JPEG_MAX_WIDTH",
    )
    notify_alert_jpeg_quality: int = Field(
        default=75,
        alias="NOTIFY_ALERT_JPEG_QUALITY",
    )
    notify_http_timeout_seconds: float = Field(
        default=30.0,
        alias="NOTIFY_HTTP_TIMEOUT_SECONDS",
    )

    # --- RTSP / IP cameras (FASE 11) ---
    rtsp_transport: str = Field(default="tcp", alias="RTSP_TRANSPORT")
    rtsp_buffer_size: int = Field(default=1, alias="RTSP_BUFFER_SIZE")
    rtsp_reconnect_delay_seconds: float = Field(
        default=3.0,
        alias="RTSP_RECONNECT_DELAY_SECONDS",
    )
    rtsp_read_failures_before_reconnect: int = Field(
        default=3,
        alias="RTSP_READ_FAILURES_BEFORE_RECONNECT",
    )
    rtsp_warmup_seconds: float = Field(default=3.0, alias="RTSP_WARMUP_SECONDS")
    rtsp_transport_fallback: bool = Field(
        default=True,
        alias="RTSP_TRANSPORT_FALLBACK",
    )
    rtsp_probe_timeout_seconds: float = Field(
        default=5.0,
        alias="RTSP_PROBE_TIMEOUT_SECONDS",
    )
    rtsp_use_ffmpeg_first: bool = Field(
        default=True,
        alias="RTSP_USE_FFMPEG_FIRST",
    )
    rtsp_ffmpeg_output_max_width: int = Field(
        default=640,
        alias="RTSP_FFMPEG_OUTPUT_MAX_WIDTH",
    )
    rtsp_ffmpeg_read_timeout_seconds: float = Field(
        default=30.0,
        alias="RTSP_FFMPEG_READ_TIMEOUT_SECONDS",
    )
    ip_webcam_prefer_http: bool = Field(
        default=True,
        alias="IP_WEBCAM_PREFER_HTTP",
    )

    @property
    def detection_class_set(self) -> frozenset[str]:
        """Allowed detection classes; empty set means "all classes"."""
        return frozenset(
            item.strip() for item in self.detection_classes.split(",") if item.strip()
        )

    @property
    def event_long_presence_class_set(self) -> frozenset[str]:
        return frozenset(
            item.strip()
            for item in self.event_long_presence_classes.split(",")
            if item.strip()
        )

    @property
    def event_abandoned_class_set(self) -> frozenset[str]:
        return frozenset(
            item.strip()
            for item in self.event_abandoned_classes.split(",")
            if item.strip()
        )

    @property
    def rule_animal_class_set(self) -> frozenset[str]:
        return frozenset(
            item.strip() for item in self.rule_animal_classes.split(",") if item.strip()
        )

    @property
    def notify_event_type_set(self) -> frozenset[str]:
        """Allowed event types for notifications; empty means all eligible types."""
        return frozenset(
            item.strip()
            for item in self.notify_event_types.split(",")
            if item.strip()
        )

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_testing(self) -> bool:
        return self.app_env == "testing"

    @property
    def async_database_url(self) -> str:
        if self.database_url.startswith("postgresql+asyncpg://"):
            return self.database_url
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace(
                "postgresql://",
                "postgresql+asyncpg://",
                1,
            )
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
