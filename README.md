# Telegram Video Downloader Bot

بوت تيليجرام لتنزيل فيديوهات TikTok وInstagram وYouTube بأفضل جودة متاحة باستخدام Python و `yt-dlp`.

## ماذا يفعل البوت؟

يرسل المستخدم رابط فيديو إلى البوت، فيتحقق البوت من أن الرابط من منصة مدعومة، ثم يستخدم `yt-dlp` لتنزيل أفضل جودة متاحة، وبعدها يرسل الفيديو للمستخدم داخل تيليجرام.

## بخصوص العلامة المائية

البوت لا يستخدم طرقًا غير مصرّح بها لحذف العلامة المائية ولا يتجاوز DRM أو حماية المنصات. إذا كانت نسخة بدون علامة مائية متاحة من المصدر نفسه أو من الصيغ التي يستطيع `yt-dlp` الوصول إليها بشكل مشروع، فقد يتم تنزيلها. أما إذا كانت العلامة المائية مدمجة داخل ملف الفيديو المتاح، فلن يقوم البوت بإزالتها اصطناعيًا.

استخدم البوت فقط مع المحتوى الذي تملكه أو لديك إذن بتنزيله.

## الملفات الموجودة

```text
telegram_video_bot/
├── bot.py              # ملف تشغيل البوت الرئيسي
├── config.py           # ملف الإعدادات المركزي
├── requirements.txt    # مكتبات Python المطلوبة
├── .env.example        # مثال ملف الإعدادات
├── .gitignore          # ملفات يتم تجاهلها عند رفع المشروع
├── run.sh              # سكربت تشغيل سريع على Linux/VPS
└── README.md           # شرح الاستخدام
```

## المتطلبات

- Python 3.10 أو أحدث.
- توكن بوت من `@BotFather`.
- يفضّل تثبيت `ffmpeg` للحصول على دمج أفضل للصوت والفيديو.

على Ubuntu/Debian:

```bash
sudo apt update
sudo apt install -y ffmpeg python3 python3-venv python3-pip
```

## الحصول على توكن البوت

افتح تيليجرام وابحث عن:

```text
@BotFather
```

ثم أرسل:

```text
/newbot
```

بعد إنشاء البوت سيعطيك توكن. ضعه في ملف `.env`.

## التشغيل السريع

ادخل إلى مجلد المشروع:

```bash
cd telegram_video_bot
```

شغّل السكربت:

```bash
./run.sh
```

في أول تشغيل سيقوم السكربت بإنشاء ملف `.env` من `.env.example` ثم سيطلب منك تعديل التوكن. افتح الملف:

```bash
nano .env
```

وضع التوكن هنا:

```env
TELEGRAM_BOT_TOKEN=ضع_توكن_البوت_هنا
```

ثم شغّل مرة أخرى:

```bash
./run.sh
```

## التشغيل اليدوي

```bash
cd telegram_video_bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env
python bot.py
```

## شرح ملف config.py

ملف `config.py` هو المسؤول عن قراءة الإعدادات من `.env`، ومنها:

- `TELEGRAM_BOT_TOKEN`: توكن بوت تيليجرام.
- `MAX_FILE_MB`: أقصى حجم للفيديو قبل رفض الإرسال.
- `DOWNLOAD_FORMAT`: صيغة الجودة المستخدمة بواسطة `yt-dlp`.
- `MERGE_OUTPUT_FORMAT`: صيغة الدمج النهائية، افتراضيًا `mp4`.
- `CLEANUP_DOWNLOADS`: حذف الملفات المؤقتة بعد الإرسال.

## تحديث yt-dlp

إذا توقفت منصة عن العمل، حدّث المكتبة:

```bash
source venv/bin/activate
pip install -U yt-dlp
```

## تشغيل دائم على VPS باستخدام tmux

```bash
sudo apt install -y tmux
tmux new -s video-bot
cd telegram_video_bot
./run.sh
```

للخروج مع إبقاء البوت يعمل:

```text
Ctrl+B ثم D
```

للعودة:

```bash
tmux attach -t video-bot
```

## ملاحظات مهمة

روابط Instagram الخاصة أو التي تحتاج تسجيل دخول قد لا تعمل. فيديوهات YouTube الكبيرة قد تتجاوز حد الإرسال في تيليجرام. المنصات تغير أنظمتها باستمرار، لذلك قد تحتاج إلى تحديث `yt-dlp` دوريًا.
