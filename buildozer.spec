[app]
title = Vosoghi Scanner
package.name = vosoghiscanner
package.domain = org.vosoghi
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 8.0

# در این خط، کتابخانه‌های مورد نیاز کدهای شما را دقیقاً وارد کردیم
requirements = python3,kivy,aiohttp,aiohttp_socks,attrs,multidict,yarl,async_timeout,idna

orientation = portrait
fullscreen = 0
android.archs = armeabi-v7a, arm64-v8a
android.allow_backup = True

# دسترسی به اینترنت برای اسکن شبکه کاملاً ضروری است
android.permissions = INTERNET
