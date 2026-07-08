#!/usr/bin/env bash
# Download paywalled papers via Safari logged-in session (AppleScript + in-page fetch)
set -euo pipefail

REF_DIR="$(cd "$(dirname "$0")/.." && pwd)/reference/papers"
mkdir -p "$REF_DIR"

# id|doi_url|fallback_search
PAPERS=(
  "freedom-prompting-reactance|https://doi.org/10.1080/01463373.2021.1920443"
  "prt-politeness|https://doi.org/10.1080/03637751.2026.2615230"
  "avert|https://doi.org/10.1109/ithet61869.2024.10837675"
  "socratic-mind|https://doi.org/10.1145/3657604.3664661"
  "crowdsourcing-trapping|https://doi.org/10.1145/3184558.3191545"
  "divide-and-inform|https://doi.org/10.2308/accr-51707"
  "deceptively-dodging|https://doi.org/10.1177/1750481318766923"
  "zero-shot-socratic|https://open.bu.edu/items/e86b12c8-5086-40f3-8086-54cce82f43fb"
)

find_pdf_url() {
  local url="$1"
  osascript <<EOF
tell application "Safari"
  activate
  if (count of windows) = 0 then make new document
  tell window 1
    set current tab to (make new tab with properties {URL:"$url"})
  end tell
  delay 12
  set js to "
    (function(){
      function abs(h){ try { return new URL(h, location.href).href; } catch(e){ return h; } }
      var links = Array.from(document.querySelectorAll('a[href]'));
      var pdfs = links.filter(function(a){
        var h = (a.href||'').toLowerCase();
        var t = (a.textContent||'').toLowerCase();
        return h.includes('.pdf') || h.includes('/pdf') || h.includes('pdfdirect')
          || h.includes('download') && (t.includes('pdf') || h.includes('pdf'))
          || t === 'pdf' || t.includes('view pdf') || t.includes('download pdf');
      }).map(function(a){ return abs(a.href); });
      if (pdfs.length) return pdfs[0];
      var metas = Array.from(document.querySelectorAll('meta[name=citation_pdf_url], meta[property=citation_pdf_url]'));
      if (metas.length) return metas[0].content;
      var ifr = document.querySelector('iframe[src*=\"pdf\"]');
      if (ifr) return abs(ifr.src);
      return '';
    })();
  "
  set pdfUrl to do JavaScript js in current tab of window 1
  close current tab
  return pdfUrl
end tell
EOF
}

download_via_safari_fetch() {
  local url="$1" out="$2"
  osascript <<EOF
tell application "Safari"
  activate
  if (count of windows) = 0 then make new document
  tell window 1
    set current tab to (make new tab with properties {URL:"$url"})
  end tell
  delay 12
  set js to "
    (function(){
      function abs(h){ try { return new URL(h, location.href).href; } catch(e){ return h; } }
      var links = Array.from(document.querySelectorAll('a[href]'));
      var pdfs = links.filter(function(a){
        var h = (a.href||'').toLowerCase();
        var t = (a.textContent||'').toLowerCase();
        return h.includes('.pdf') || h.includes('/pdf') || h.includes('pdfdirect')
          || (h.includes('download') && (t.includes('pdf') || h.includes('pdf')))
          || t === 'pdf' || t.includes('view pdf') || t.includes('download pdf')
          || t.includes('accepted manuscript');
      }).map(function(a){ return abs(a.href); });
      var pdf = pdfs[0] || '';
      var metas = Array.from(document.querySelectorAll('meta[name=citation_pdf_url]'));
      if (!pdf && metas.length) pdf = metas[0].content;
      if (!pdf) return 'NO_PDF';
      return fetch(pdf, {credentials:'include'})
        .then(function(r){ if(!r.ok) throw new Error('HTTP '+r.status); return r.arrayBuffer(); })
        .then(function(buf){
          var bytes = new Uint8Array(buf);
          var bin = '';
          for (var i=0;i<bytes.length;i++) bin += String.fromCharCode(bytes[i]);
          return 'B64:' + btoa(bin);
        })
        .catch(function(e){ return 'ERR:'+e.message; });
    })();
  "
  set result to do JavaScript js in current tab of window 1
  close current tab
  if result starts with "B64:" then
    set b64 to text 5 thru -1 of result
    do shell script "echo " & quoted form of b64 & " | base64 -D > " & quoted form of "$out"
    return "OK"
  else
    return result
  end if
end tell
EOF
}

for entry in "${PAPERS[@]}"; do
  id="${entry%%|*}"
  url="${entry#*|}"
  out="$REF_DIR/${id}.pdf"
  if [[ -f "$out" ]] && [[ $(wc -c < "$out" | tr -d ' ') -gt 10000 ]]; then
    echo "[skip] $id ($(wc -c < "$out") bytes)"
    continue
  fi
  echo "[safari] $id <- $url"
  result=$(download_via_safari_fetch "$url" "$out" 2>&1) || result="ERR:osascript failed"
  if [[ -f "$out" ]] && [[ $(wc -c < "$out" | tr -d ' ') -gt 10000 ]]; then
    echo "[ok] $id ($(wc -c < "$out") bytes)"
  else
    rm -f "$out"
    echo "[fail] $id: $result"
    pdf_url=$(find_pdf_url "$url" 2>/dev/null || true)
    if [[ -n "$pdf_url" && "$pdf_url" != "missing value" ]]; then
      echo "  found pdf url: $pdf_url"
    fi
  fi
  sleep 2
done

echo "=== Done ==="
ls -lh "$REF_DIR"/*.pdf 2>/dev/null || true
