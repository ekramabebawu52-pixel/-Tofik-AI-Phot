

[app]

title = Tofik AI Photo
package.name = tofikai
package.domain = org.tofik

source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,webp

version = 2.0

requirements = python3,kivy,pillow,plyer

orientation = portrait
fullscreen = 0

android.permissions = READ_MEDIA_IMAGES
android.api = 35
android.minapi = 23
android.ndk = 27c
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

[buildozer]

log_level = 2
warn_on_root = 1
