#!/usr/bin/env bash
# Lab performance baseline (Lighthouse, mobile + desktop). Lab data, not real-user Core Web Vitals.
#   seo/lighthouse.sh OUTDIR URL...      (needs lighthouse in $LH_BIN, Chromium in $CHROME_PATH)
set -u
out=$1; shift; mkdir -p "$out"
: "${CHROME_PATH:=/opt/pw-browsers/chromium-1194/chrome-linux/chrome}"; export CHROME_PATH
for url in "$@"; do
  slug=$(echo "$url" | sed -E 's#https?://[^/]+/##; s#/$##; s#[/?=&]#_#g'); slug=${slug:-home}
  for mode in mobile desktop; do
    extra=(); [ "$mode" = desktop ] && extra=(--preset=desktop)
    for run in 1 2 3; do
      "$LH_BIN" "$url" "${extra[@]}" --only-categories=performance,seo,accessibility,best-practices --output=json --quiet \
        --output-path="$out/$slug.$mode.$run.json" --chrome-flags="--headless=new --no-sandbox --ignore-certificate-errors" \
        --max-wait-for-load=60000 >/dev/null 2>&1 || echo "fail $url $mode $run"
    done
  done
done
