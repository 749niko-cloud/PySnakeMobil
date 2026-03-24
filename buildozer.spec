[app]
# (str) Title of your application
title = PySnakeMobil

# (str) Package name
package.name = pysnakemobil

# (str) Package domain (unique)
package.domain = org.snakemobil

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
android.arch = armeabi-v7a,arm64-v8a

# Python for Android - use pygame bootstrap
p4a.bootstrap = pygame
p4a.branch = master

# Buildozer command target logic
# debug: buildozer android debug
# release: buildozer android release

[buildozer]
log_level = 2
warn_on_root = 1
