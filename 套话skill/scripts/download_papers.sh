#!/usr/bin/env bash
# 论文下载：优先 arXiv export + IEEE document + 作者主页，不走出版商 DOI 跳转
set -euo pipefail
REF_DIR="$(cd "$(dirname "$0")/.." && pwd)/reference/papers"
mkdir -p "$REF_DIR"

download() {
  local id="$1" url="$2"
  local out="$REF_DIR/${id}.pdf"
  [[ -f "$out" && $(wc -c < "$out" | tr -d ' ') -gt 10000 ]] && { echo "[skip] $id"; return 0; }
  echo "[dl] $id <- $url"
  curl -fsSL --max-time 120 -L -A "Mozilla/5.0" -o "$out" "$url" && \
    [[ $(wc -c < "$out" | tr -d ' ') -gt 10000 ]] && echo "[ok] $id" || { rm -f "$out"; echo "[fail] $id"; return 1; }
}

# === arXiv ===
download productagent "https://aclanthology.org/2025.emnlp-industry.25.pdf"
download do-people-ask-good-questions "https://www.cs.princeton.edu/~bl8144/papers/RotheEtAl2018CompBrainBehavior.pdf"
download user-intent-slreview "https://export.arxiv.org/pdf/2308.08496v1.pdf"
download intellichain "https://arxiv.org/pdf/2502.00010"
download socratic-mind "https://arxiv.org/pdf/2509.16262"
download socratic-hard-problem "https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2026.1757622/pdf"
download prt-politeness-arxiv "https://arxiv.org/pdf/2601.20683"  # reactance×politeness 近缘 2026

# === 开放仓库 / 作者页 ===
download children-info-search "http://jonathandnelson.com/papers/2014childrensInformation.pdf"
download optimal-info-disclosure "http://www.kolotilin.com/papers/disclosure.pdf"
download socratic-virtue-ethics "https://ojs.aaai.org/index.php/AIES/article/download/36748/38886/40823"
download zero-shot-socratic "https://kevingold.site/GoldGengAIET24-10.pdf"
download crowdsourcing-trapping "https://www.deutsche-telekom-laboratories.de/~moeller/publications/Jimenez2018WWW.pdf" || true
curl -kfsSL -L -o "$REF_DIR/crowdsourcing-trapping.pdf" "https://www.deutsche-telekom-laboratories.de/~moeller/publications/Jimenez2018WWW.pdf" 2>/dev/null || true
download trapping-interspeech-2015 "https://www.isca-archive.org/interspeech_2015/naderi15_interspeech.pdf"

# === IEEE（需机构订阅；curl 常 418，请 Safari 打开后另存为 avert.pdf）===
# download avert "https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10837675"

echo "=== $(ls "$REF_DIR"/*.pdf 2>/dev/null | wc -l | tr -d ' ') PDFs ==="
ls -lh "$REF_DIR"/*.pdf 2>/dev/null
