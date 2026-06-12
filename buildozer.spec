[app]
title = Vosoghi Scanner
package.name = vosoghiscanner
package.domain = org.vosoghi
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 8.0

# پیش‌نیازهای حیاتی و فیکس شده برای اسکنر همزمان شما
requirements = python3==3.10.11,kivy==2.3.0,aiohttp,aiohttp_socks,attrs,multidict,yarl,async_timeout,idna,charset-normalizer

orientation = portrait
fullscreen = 0

# تمرکز روی پردازنده‌های مدرن اندروید برای بیلد سریع‌تر و بدون خطا
android.archs = arm64-v8a
android.allow_backup = True

# مجوزهای لازم اندروید برای دسترسی به شبکه و اسکن آی‌پی‌ها
android.permissions = INTERNET, ACCESS_NETWORK_STATE

# تنظیمات نسخه اندروید منطبق با کتابخانه‌ها
android.api = 33
android.minapi = 21
android.ndk_api = 21

[buildozer]
log_level = 2
warn_on_root = 1
