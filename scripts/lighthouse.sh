#!/usr/bin/env bash
# Lighthouse kapısı: Perf>=85 A11y>=95 BP>=90 SEO>=90
set -euo pipefail
LH=/run/media/dorukersoy/8C3A1DA03A1D87FA/data/qa_tmp/node_modules/.bin/lighthouse
CHROME_PATH="${CHROME_PATH:-$(find /home/dorukersoy/.cache/ms-playwright -type f -name chrome | head -1)}"
CHROME_PATH="$CHROME_PATH" "$LH" http://localhost:80/ --quiet \
  --chrome-flags="--headless --no-sandbox" --output=json --output-path=docs/lighthouse.json \
  --only-categories=performance,accessibility,best-practices,seo >/dev/null
python3 - <<'PY'
import json
d=json.load(open("docs/lighthouse.json"))
s={k:round(v["score"]*100) for k,v in d["categories"].items()}
print("Lighthouse:", s)
esik={"performance":85,"accessibility":95,"best-practices":90,"seo":90}
for k,v in esik.items():
    if s.get(k,0)<v: raise SystemExit(f"KIRMIZI: {k}={s.get(k)} < {v}")
print("YEŞİL")
PY
