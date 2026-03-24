[app]
title = PySnakeMobil
package.name = pysnakemobil
package.domain = org.snakemobil
version = 1.0.0
# optional für Semver:
# version.regex = ^(\d+\.\d+\.\d+)$

# Icon & startbild (für Build und Store)
icon.filename = icon.png
# optional: start image für Ladebildschirm
presplash.filename = presplash.png

# (str) Source code where the main.py is located
source.dir = .
source.include_exts = py,png,jpg,kv

# (list) Application requirements
requirements = python3,pygame,numpy

# (str) Supported orientation: landscape, portrait or all
orientation = portrait

# (list) Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_COARSE_LOCATION,ACCESS_FINE_LOCATION,MODIFY_AUDIO_SETTINGS,VIBRATE,CAMERA

# (int) Android API to use
android.api = 33
android.minapi = 21
android.archs = armeabi-v7a,arm64-v8a

# Use SDL2 bootstrap (not the removed pygame bootstrap)
p4a.bootstrap = sdl2
p4a.branch = release-2022.12.20
log_level = 2
warn_on_root = 1
