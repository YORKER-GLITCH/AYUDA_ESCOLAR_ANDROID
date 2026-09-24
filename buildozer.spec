[app]
title = AYUDA ESCOLAR
package.name = ayudaescolar
package.domain = org.yorkito
source.dir = .
source.include_exts = py,json,png,jpg,kv
version = 1.0.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[app:android]
android.api = 35
android.minapi = 23
android.archs = arm64-v8a
android.allow_backup = True
android.private_storage = True
