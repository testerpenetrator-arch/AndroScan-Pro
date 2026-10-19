#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ANDROID_DIR="$ROOT/android-client"

if ! command -v java >/dev/null 2>&1; then
  echo "ERROR: Java/JDK 17 no está instalado o no está en PATH." >&2
  exit 2
fi
if ! command -v gradle >/dev/null 2>&1; then
  echo "ERROR: Gradle no está en PATH. Abre android-client en Android Studio o instala Gradle 8.9." >&2
  exit 2
fi
if [[ -z "${ANDROID_HOME:-}${ANDROID_SDK_ROOT:-}" ]]; then
  echo "ERROR: define ANDROID_HOME o ANDROID_SDK_ROOT con la ruta del Android SDK." >&2
  exit 2
fi

cd "$ANDROID_DIR"
gradle assembleDebug --no-daemon
APK="$ANDROID_DIR/app/build/outputs/apk/debug/app-debug.apk"
if [[ ! -s "$APK" ]]; then
  echo "ERROR: Gradle terminó pero no se encontró el APK esperado: $APK" >&2
  exit 3
fi
sha256sum "$APK"
printf '\nAPK compilado: %s\n' "$APK"
