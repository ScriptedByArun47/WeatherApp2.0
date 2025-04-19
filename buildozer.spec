[app]

# App metadata
title = WeatherX
package.name = weatherx
package.domain = org.yourdomain
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,mp4,json
version = 1.0
requirements = python3,kivy,kivymd,plyer,requests
orientation = portrait

# Entry point
main.py = main.py

# Permissions for GPS, internet, and storage
android.permissions = INTERNET, ACCESS_COARSE_LOCATION, ACCESS_FINE_LOCATION, WAKE_LOCK

# Include all assets
android.include_exts = mp4,png,jpg,json,ttf

# Supported Android architectures
android.archs = armeabi-v7a, arm64-v8a

# Minimum Android API level
android.minapi = 21
android.target = 30

# Fullscreen mode
fullscreen = 1

# Hide the default ActionBar
android.hide_statusbar = 1

# Adaptive icon
android.icon = assets/icons/icon.png
android.round_icon = assets/icons/icon.png

# Enable AndroidX (required for newer libraries)
android.enable_androidx = 1

# Keep screen on while running
android.wakelock = True

# Video support via ffpyplayer (or you can use other methods if needed)
# requirements = python3,kivy,kivymd,plyer,requests,ffpyplayer
# ffpyplayer is optional and may be replaced by your Kivy Video component method

# Additional Java .jar or .so libraries if needed
# android.add_jars =

# For debugging logs
log_level = 2

[buildozer]
log_level = 2
warn_on_root = 1
