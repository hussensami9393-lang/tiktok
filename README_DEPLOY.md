# نشر البوت على Fly.io

إذا ظهر خطأ مثل:

```text
Failed to fetch image or build from source: unauthorized
```

فغالبًا السبب أن المنصة حاولت استخدام صورة Docker غير متاحة أو أن إعدادات البناء غير مكتملة. هذه النسخة تحتوي على `Dockerfile` و `fly.toml` و `Procfile`.

## خطوات النشر على Fly.io

ثبت flyctl وسجل الدخول:

```bash
fly auth login
```

ادخل إلى مجلد المشروع:

```bash
cd telegram_video_bot
```

أنشئ التطبيق أو غيّر اسم التطبيق داخل `fly.toml` إلى اسم فريد خاص بك:

```toml
app = "your-unique-bot-name"
```

ضع توكن البوت كـ Secret ولا تضعه داخل GitHub:

```bash
fly secrets set TELEGRAM_BOT_TOKEN="ضع_توكن_البوت_هنا"
```

ثم انشر:

```bash
fly deploy
```

## ملاحظات مهمة

هذا البوت يعمل كـ worker عبر polling، وليس Web Server، لذلك لا يحتاج إلى منفذ HTTP. إذا كانت منصة النشر تتطلب Web Service دائمًا فقد تحتاج إلى اختيار نوع Worker أو Background Service.

إذا فشل البناء بسبب اسم التطبيق، غيّر قيمة `app` في `fly.toml` لأن الاسم يجب أن يكون فريدًا عالميًا.

إذا فشل تنزيل فيديوهات من منصة معينة، حدّث `yt-dlp` داخل `requirements.txt` أو أعد البناء لاحقًا لأن المنصات تغير آلياتها باستمرار.
