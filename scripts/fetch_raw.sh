#!/usr/bin/env bash
# Re-fetch the raw files listed in data/raw/MANIFEST.csv, then compare sha256 with the manifest.
# Pages change; a different hash means the source changed since 2026-10-12 and figures need re-checking.
set -euo pipefail
cd "$(dirname "$0")/../data/raw"
UA="Mozilla/5.0 (compatible; ai-careers-eda research; +https://github.com/Earnearn-aram/ai-careers-eda)"
tail -n +2 MANIFEST.csv | while IFS=, read -r path url retrieved sha; do
  mkdir -p "$(dirname "$path")"; curl -sSL --compressed -A "$UA" -o "$path" "$url"
  now=$(sha256sum "$path" | cut -d' ' -f1); [ "$now" = "$sha" ] && s=same || s=CHANGED; echo "$s $path"
done
