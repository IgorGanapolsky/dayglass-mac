#!/usr/bin/env bash
# Dayglass — 1-Command macOS Installer
# Usage: curl -fsSL https://www.dayglass.io/install.sh | bash
set -euo pipefail

BASE_URL="https://github.com/IgorGanapolsky/dayglass-mac/releases/latest/download"
DMG_URL="${BASE_URL}/Dayglass.dmg"
VERSION="latest"
APP_DEST="${DAYGLASS_INSTALL_APP_DIR:-/Applications/Dayglass.app}"
TMP_DMG="$(mktemp /tmp/Dayglass-installer-XXXXXX.dmg)"
MOUNT_DIR="$(mktemp -d /tmp/Dayglass-mount-XXXXXX)"

cleanup() {
  hdiutil detach "${MOUNT_DIR}" -quiet 2>/dev/null || true
  rm -rf "${TMP_DMG}" "${MOUNT_DIR}" 2>/dev/null || true
}
trap cleanup EXIT

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "Error: Dayglass requires macOS (Darwin)." >&2
  exit 1
fi

if [[ "$(sysctl -n hw.optional.arm64 2>/dev/null)" != "1" ]]; then
  echo "Error: Dayglass needs an Apple silicon Mac. Nothing was installed." >&2
  exit 1
fi

if [[ "$(sw_vers -productVersion | cut -d. -f1)" -lt 14 ]]; then
  echo "Error: Dayglass needs macOS 14 (Sonoma) or later. Nothing was installed." >&2
  exit 1
fi

echo "==> [1/4] Downloading the latest Dayglass for macOS..."
curl -fL --progress-bar "${DMG_URL}" -o "${TMP_DMG}"

echo "==> [2/4] Verifying SHA-256 checksum..."
EXPECTED_SHA256="$(curl -fsSL "${BASE_URL}/SHA256SUMS" | awk '$2=="Dayglass.dmg"{print $1}')"
if [[ -z "${EXPECTED_SHA256}" ]]; then
  echo "Error: could not read SHA256SUMS for the latest release." >&2
  exit 1
fi
ACTUAL_SHA256="$(shasum -a 256 "${TMP_DMG}" | awk '{print $1}')"
if [[ "${ACTUAL_SHA256}" != "${EXPECTED_SHA256}" ]]; then
  echo "Error: SHA-256 mismatch! Expected ${EXPECTED_SHA256}, got ${ACTUAL_SHA256}" >&2
  exit 1
fi

echo "==> [3/4] Checking Apple notarization and installing Dayglass.app to ${APP_DEST}..."
rmdir "${MOUNT_DIR}" 2>/dev/null || true
hdiutil attach "${TMP_DMG}" -nobrowse -readonly -mountpoint "${MOUNT_DIR}" -quiet
# Gatekeeper decides, not this script: the app must be Developer ID signed and notarized by Apple.
# Nothing is replaced when it is not.
if ! codesign --verify --deep --strict "${MOUNT_DIR}/Dayglass.app" 2>/dev/null \
  || ! spctl --assess --type execute "${MOUNT_DIR}/Dayglass.app" 2>/dev/null; then
  echo "Error: this Dayglass build is not signed and notarized by Apple. Nothing was installed." >&2
  exit 1
fi
rm -rf "${APP_DEST}"
cp -R "${MOUNT_DIR}/Dayglass.app" "${APP_DEST}"
hdiutil detach "${MOUNT_DIR}" -quiet || true

echo "==> [4/4] Registering Dayglass with LaunchServices..."
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "${APP_DEST}" 2>/dev/null || true

# Anonymous install telemetry ping to PostHog
curl -fsS -m 3 -X POST "https://us.i.posthog.com/capture/" \
  -H "Content-Type: application/json" \
  -d "{\"api_key\":\"phc_ub5A4JPFsB2dm54Vaq2dWGeDh9zouzLL4Vb6TcicJxvf\",\"event\":\"app_installed_via_script\",\"distinct_id\":\"dg-cli-$(uuidgen | tr '[:upper:]' '[:lower:]' | cut -c1-12)\",\"properties\":{\"version\":\"${VERSION}\",\"arch\":\"$(uname -m)\",\"utm_source\":\"install_sh\"}}" >/dev/null 2>&1 || true

echo ""
echo "✅ Dayglass installed at ${APP_DEST}"
if [[ "${DAYGLASS_NO_OPEN:-0}" != "1" ]]; then
  echo "==> Launching Dayglass.app..."
  open "${APP_DEST}" || true
fi
