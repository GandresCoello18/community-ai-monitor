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
        default=True,
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
