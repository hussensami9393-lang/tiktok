import asyncio
import logging
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from yt_dlp import YoutubeDL

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8227316888:AAFudkVYoz8uCsGcuV3tSkHd4lbpL_JOAtU").strip()
MAX_FILE_MB = int(os.getenv("MAX_FILE_MB", "49"))
MAX_FILE_BYTES = MAX_FILE_MB * 1024 * 1024

SUPPORTED_DOMAINS = (
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
)

URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("telegram-video-bot")


def extract_url(text: str) -> Optional[str]:
    match = URL_RE.search(text or "")
    if not match:
        return None
    return match.group(0).strip().rstrip(").,؛،!")


def is_supported_url(url: str) -> bool:
    lowered = url.lower()
    return any(domain in lowered for domain in SUPPORTED_DOMAINS)


def human_size(num_bytes: int) -> str:
    value = float(num_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if value < 1024 or unit == "GB":
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} GB"


def find_downloaded_video(work_dir: Path) -> Optional[Path]:
    candidates = []
    for path in work_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".mp4", ".mkv", ".webm", ".mov", ".m4v"}:
            candidates.append(path)
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_size)


def download_video_sync(url: str, work_dir: Path) -> tuple[Path, dict]:
    output_template = str(work_dir / "%(title).120s_%(id)s.%(ext)s")

    ydl_opts = {
        "outtmpl": output_template,
        "format": "bv*+ba/bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "prefer_ffmpeg": True,
        "retries": 3,
        "fragment_retries": 3,
        "socket_timeout": 30,
        # ملاحظة: لا نستخدم خيارات لتجاوز DRM أو حماية الوصول أو انتهاك حقوق المنصات.
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    video_path = find_downloaded_video(work_dir)
    if not video_path:
        raise RuntimeError("لم أتمكن من العثور على ملف الفيديو بعد التنزيل.")

    return video_path, info or {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "أهلًا بك! 👋\n\n"
        "أرسل رابط فيديو من TikTok أو Instagram أو YouTube وسأحاول تنزيله لك بأفضل جودة متاحة.\n\n"
        "ملاحظات مهمة:\n"
        "• استخدم البوت فقط مع المحتوى الذي تملكه أو لديك إذن بتنزيله.\n"
        "• لا يمكنني تجاوز DRM أو القيود الخاصة أو إزالة علامات مائية بطرق غير مصرّح بها.\n"
        "• إذا توفرت نسخة بدون علامة مائية من المصدر نفسه فسيحاول yt-dlp جلب أفضل نسخة متاحة.\n"
        f"• الحد الحالي لحجم الإرسال: {MAX_FILE_MB}MB."
    )
    await update.message.reply_text(text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start(update, context)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    url = extract_url(update.message.text)
    if not url:
        await update.message.reply_text("أرسل رابط فيديو مباشر من TikTok أو Instagram أو YouTube.")
        return

    if not is_supported_url(url):
        await update.message.reply_text("هذا الرابط غير مدعوم حاليًا. المنصات المدعومة: TikTok وInstagram وYouTube.")
        return

    status_msg = await update.message.reply_text("جاري تجهيز الفيديو... ⏳")
    await update.message.chat.send_action(ChatAction.UPLOAD_VIDEO)

    work_dir_path = Path(tempfile.mkdtemp(prefix="video_bot_"))
    try:
        video_path, info = await asyncio.to_thread(download_video_sync, url, work_dir_path)
        file_size = video_path.stat().st_size

        title = info.get("title") or "video"
        uploader = info.get("uploader") or info.get("channel") or "غير معروف"
        caption = f"✅ تم التنزيل\nالعنوان: {title[:120]}\nالمصدر: {uploader}"

        if file_size > MAX_FILE_BYTES:
            await status_msg.edit_text(
                "تم تنزيل الفيديو، لكن حجمه أكبر من الحد المسموح لإرساله عبر البوت.\n"
                f"الحجم: {human_size(file_size)}\n"
                "جرّب فيديو أقصر أو ارفع حد MAX_FILE_MB إذا كان حساب البوت لديك يسمح بذلك."
            )
            return

        await status_msg.edit_text("تم التنزيل، جاري الإرسال... 📤")
        with video_path.open("rb") as video_file:
            await update.message.reply_video(
                video=video_file,
                caption=caption,
                supports_streaming=True,
                read_timeout=120,
                write_timeout=120,
                connect_timeout=30,
                pool_timeout=30,
            )
        await status_msg.delete()

    except Exception as exc:
        logger.exception("Download failed")
        await status_msg.edit_text(
            "تعذر تنزيل الفيديو. قد يكون الرابط خاصًا، أو يتطلب تسجيل دخول، أو غير متاح في المنطقة، "
            "أو أن المنصة غيّرت طريقة الوصول.\n\n"
            f"التفاصيل التقنية: {str(exc)[:500]}"
        )
    finally:
        shutil.rmtree(work_dir_path, ignore_errors=True)


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise SystemExit("يرجى إنشاء ملف .env ووضع TELEGRAM_BOT_TOKEN داخله.")

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot started")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
