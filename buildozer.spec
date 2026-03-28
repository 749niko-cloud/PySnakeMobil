[app]
title = PySnakeMobil
package.name = pysnakemobil
package.domain = org.snakemobil
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,wav,ogg
version = 0.1

# Requirements: pygame is essential. 
# python3 and android are handled by the p4a recipes.
requirements = python3,pygame==2.5.2,android

orientation = portrait
fullscreen = 1
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# Permissions: Needed for saving screenshots and core functionality
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET

# Icon and Presplash (using your icon.png for both)
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/icon.png

# Android API levels (Play Store requires Target API 34+ for new apps)
android.api = 34
android.minapi = 21
android.ndk = 25b

# Standard buildozer requirements for p4a
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1

# Release settings (Use these when you are ready for the Play Store)
# android.release_artifact = aab
# android.keystore = /home/user/keys/mykey.keystore
# android.keystore_password = password
# android.keyalias = alias
# android.keyalias_password = password