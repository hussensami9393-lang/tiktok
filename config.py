import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class BotConfig:
    telegram_bot_token: str
    max_file_mb: int
    max_file_bytes: int
    supported_domains: tuple[str, ...]
    download_format: str
    merge_output_format: str
    cleanup_downloads: bool


def get_bool_env(name: str, default: bool = True) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def load_config() -> BotConfig:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "8227316888:AAFudkVYoz8uCsGcuV3tSkHd4lbpL_JOAtU").strip()
    max_file_mb = int(os.getenv("MAX_FILE_MB", "49"))

    return BotConfig(
        telegram_bot_token=token,
        max_file_mb=max_file_mb,
        max_file_bytes=max_file_mb * 1024 * 1024,
        supported_domains=(
            "tiktok.com",
            "vm.tiktok.com",
            "vt.tiktok.com",
            "instagram.com",
            "www.instagram.com",
            "youtube.com",
            "www.youtube.com",
            "youtu.be",
            "m.youtube.com",
            "music.youtube.com",
        ),
        download_format=os.getenv("DOWNLOAD_FORMAT", "bv*+ba/bestvideo+bestaudio/best"),
        merge_output_format=os.getenv("MERGE_OUTPUT_FORMAT", "mp4"),
        cleanup_downloads=get_bool_env("CLEANUP_DOWNLOADS", True),
    )


CONFIG = load_config()


def validate_config() -> None:
    if not CONFIG.telegram_bot_token:
        raise SystemExit(
            "Missing TELEGRAM_BOT_TOKEN. Create a .env file from .env.example and add your bot token."
        )

    if CONFIG.max_file_mb <= 0:
        raise SystemExit("MAX_FILE_MB must be greater than 0.")
