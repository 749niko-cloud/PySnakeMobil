# PySnakeMobil - Android App

**Dein klassisches Snake-Spiel für Android!**

Vollständiges pygame-Original portiert zu Android via buildozer + python-for-android.

---

## 📱 Features

- Vollständiger Snake-Gameplay (wie p2.py)
- Sound & Musik (4 Tracks: G-BEAT, CYBER, RETRO, OFF)
- Top-10 Highscores (persistent)
- Boot-Sequenz + Terminal-Animation
- Matrix-Effekt + Effekte
- Touch/Swipe-Steuerung
- Screenshot-Funktionalität
- 100% pygame Original-Code

---

## 🛠️ Vorbereitung (Windows → Android)

### 1. WSL2 Ubuntu einrichten

```bash
wsl --install Ubuntu
```

Öffne WSL Terminal:
```bash
wsl
```

### 2. Dependencies installieren

```bash
sudo apt update
sudo apt install -y python3 python3-pip git openjdk-11-jdk unzip build-essential
```

### 3. Android SDK + buildozer installieren

```bash
pip install --upgrade pip
pip install buildozer cython virtualenv
pip install python-for-android
```

Lade Android SDK herunter (minimum API 21, zielAPI 33):
```bash
mkdir -p ~/Android
cd ~/Android
wget https://dl.google.com/android/repository/platform-tools_r33.0.3-linux.zip
unzip platform-tools_r33.0.3-linux.zip
sudo apt install android-sdk-platform-tools android-sdk-build-tools
```

Umgebungsvariablen setzen:
```bash
export ANDROID_SDK_ROOT=~/.android
export ANDROID_NDK_ROOT=~/.android/ndk/25.2.8767484  # oder correct version
export PATH=$PATH:$ANDROID_SDK_ROOT/tools:$ANDROID_SDK_ROOT/platform-tools
```

### 4. Repository ins WSL klonen

```bash
cd /mnt/c/Users/jo/OneDrive/Dokumente/GitHub/PySnakeMobil
```

---

## 🚀 Build-Schritte

### Debug APK (Test)

```bash
buildozer -v android debug
```

Wenn erfolgreich:
```bash
buildozer android deploy run
```

Die App startet auf allen verbundenen Geräten.

### Release AAB (Google Play)

1. **Keystore erstellen:**
```bash
keytool -genkey -v -keystore ~/.keystore/pysnakemobil.keystore \
  -alias pysnake -keyalg RSA -keysize 2048 -validity 10000 \
  -keypass mypass123 -storepass mypass123
```

2. **buildozer.spec editieren** (Release-Keys setzen):
```ini
[app]
...

android.release_keyalias = pysnake
android.release_keystore = /home/USERNAME/.keystore/pysnakemobil.keystore
android.release_keyalias_password = mypass123
android.release_keystore_password = mypass123
```

3. **Release-Build:**
```bash
buildozer -v android release
```

Die `.aab` Datei befindet sich in:
```
bin/pysnakemobil-0.1-release.aab
```

---

## 📦 Google Play Store Upload

1. **Entwicklerkonto erstellen:** https://play.google.com/console (EUR 25 einmalig)

2. **Neue App erstellen:**
   - Name: "PySnakeMobil"
   - Package ID: `org.snakemobil.pysnakemobil` (must match buildozer.spec)
   - App-Typ: Game

3. **Metadaten ausfüllen:**
   - Screenshots (Gameplay, Startbildschirm)
   - Icon (512x512 PNG)
   - Promo-Grafik (1024x500 PNG)
   - Beschreibung
   - Privacy-Policy

4. **Release erstellen:**
   - `.aab` hochladen
   - Beta/Internal Testing → Production

5. **Genehmigung abwarten** (Google Play Prüfung ~24h)

---

## 🎮 Spielanleitung (In-Game)

- **Swipe zum Starten:** In der Kontrollzone (unten) swipen
- **Bewegung:** In beliebiger Richtung swipen (50px Mindestdistanz)
- **Essen:** Rote Quadrate sammeln = +10 Punkte
- **Musik:** Startbildschirm: OFF/RETRO/CYBER/G-BEAT wählen
- **Screenshot:** Während Gameplay verfügbar

---

## 🐛 Häufige Fehler

| Fehler | Lösung |
|--------|--------|
| `buildozer: command not found` | WSL nicht installiert oder PATH nicht gesetzt |
| `Android NDK not found` | NDK-Path in `.buildozer/android/ndk_path.txt` prüfen |
| `permission denied /dev/kvm` | VM nicht aktiviert (Windows Hyper-V) |
| `pygame not found` | `requirements` in buildozer.spec prüfen |
| `INSTALL_FAILED_INSUFFICIENT_STORAGE` | Speicher auf Gerät freigeben |

---

## 📋 Checkliste: Von Concept zum Play Store

- [x] Spiel läuft auf Windows (p2.py)
- [ ] WSL2 + Android SDK installiert
- [ ] buildozer debug getestet
- [ ] App auf echtem Phone getestet
- [ ] Keystore erstellt
- [ ] buildozer release gebaut (.aab)
- [ ] Play Developer Account erstellt
- [ ] Screenshots + Icon vorbereitet
- [ ] Privacy Policy geschrieben
- [ ] .aab hochgeladen
- [ ] In Internal Testing freigegeben
- [ ] Google-Prüfung abgewartet
- [ ] Production Live!

---

## 💬 Support

Bei Fragen zu buildozer: https://buildozer.readthedocs.io/
Bei Fragen zu python-for-android: https://python-for-android.readthedocs.io/

---

**Made by NikO with help of Gemini & buildozer magic ✨**
