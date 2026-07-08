#!/usr/bin/env bash
# Download papers cited in Readme §90-197 into reference/papers/
set -euo pipefail
REF_DIR="$(cd "$(dirname "$0")/.." && pwd)/reference/papers"
mkdir -p "$REF_DIR"

download() {
  local id="$1" url="$2" ext="${3:-pdf}"
  local out="$REF_DIR/${id}.${ext}"
  if [[ -f "$out" && -s "$out" ]]; then
    echo "[skip] $id already exists"
    return 0
  fi
  echo "[dl] $id <- $url"
  if curl -fsSL --max-time 120 -o "$out" "$url"; then
    if [[ -s "$out" ]]; then
      echo "[ok] $id ($(wc -c < "$out") bytes)"
      return 0
    fi
  fi
  rm -f "$out"
  echo "[fail] $id"
  return 1
}

# === Open-access PDFs ===
download productagent "https://aclanthology.org/2025.emnlp-industry.25.pdf"
download children-info-search "http://jonathandnelson.com/papers/2014childrensInformation.pdf"
download do-people-ask-good-questions "https://www.cs.princeton.edu/~bl8144/papers/RotheEtAl2018CompBrainBehavior.pdf"
download user-intent-slreview "https://export.arxiv.org/pdf/2308.08496v1.pdf"
download intellichain "https://arxiv.org/pdf/2502.00010"
download optimal-info-disclosure "http://www.kolotilin.com/papers/disclosure.pdf"
download socratic-virtue-ethics "https://ojs.aaai.org/index.php/AIES/article/download/36748/38886/40823"
download socratic-mind-impact "https://arxiv.org/pdf/2509.16262"
download freedom-prompting-reactance "https://www.tandfonline.com/doi/pdf/10.1080/01463373.2021.1920443" || true
download prt-overview-2026 "https://psycnet.apa.org/fulltext/2026-21323-001.pdf" || true
download zero-shot-socratic "https://open.bu.edu/bitstream/handle/2144/48938/Gold_Geng_2024_On%20the%20Helpfulness%20of%20a%20Zero-Shot%20Socratic%20Tutor.pdf?sequence=1&isAllowed=y" || true
download socratic-hard-problem "https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2026.1757622/pdf" || true
download deceptively-dodging "https://journals.sagepub.com/doi/pdf/10.1177/1750481318766923" || true
download crowdsourcing-trapping "https://dl.acm.org/doi/pdf/10.1145/3184558.3191545" || true
download divide-and-inform "https://papers.ssrn.com/sol3/Delivery.cfm?abstractid=2500000" || true

# Fallback: save abstracts for failed downloads
write_stub() {
  local id="$1" title="$2" doi="$3" abstract="$4"
  local out="$REF_DIR/${id}.stub.md"
  [[ -f "$REF_DIR/${id}.pdf" ]] && return 0
  cat > "$out" <<EOF
# $title

- DOI: $doi
- Status: PDF not openly available; stub from Readme/search

## Abstract

$abstract
EOF
  echo "[stub] $id"
}

write_stub "freedom-prompting-reactance" \
  "Freedom-prompting Reactance Mitigation Strategies" \
  "10.1080/01463373.2021.1920443" \
  "Assessed relative effects of reactance mitigation strategies (inoculation vs restoration postscript) across trait reactance levels. For high-trait-reactance recipients, inoculation reduced perceived freedom threat and increased behavioral intention."

write_stub "prt-politeness" \
  "Psychological Reactance Theory and Politeness Theory" \
  "10.1080/03637751.2026.2615230" \
  "Tests competing explanations for threat-to-freedom in persuasive resistance; integrates PRT and politeness/facework frameworks."

write_stub "avert" \
  "AVERT: LLM-Based Procedure That Interactively Verifies Understanding" \
  "10.1109/ithet61869.2024.10837675" \
  "LLM chatbot using Socratic questioning to verify code authorship and student understanding; guides explanation rather than direct questioning."

write_stub "socratic-mind" \
  "Socratic Mind: Scalable Oral Assessment Powered by AI" \
  "10.1145/3657604.3664661" \
  "GenAI virtual instructor for scalable oral assessment via Socratic questioning in large classrooms (600 students)."

write_stub "crowdsourcing-trapping" \
  "Outliers Detection vs. Control Questions in Crowdsourcing" \
  "10.1145/3184558.3191545" \
  "WWW 2018: trapping questions and outlier detection for crowdsourcing reliability; combination works best."

write_stub "divide-and-inform" \
  "Divide and Inform: Rationing Information to Facilitate Persuasion" \
  "10.2308/accr-51707" \
  "Bayesian persuasion model: selective/rationed disclosure can increase information precision when manager-user objectives misalign."

write_stub "deceptively-dodging" \
  "Deceptively Dodging Questions" \
  "10.1177/1750481318766923" \
  "IMT-based analysis of question dodging via Gricean maxims; selective/truthful-but-biased information violates quantity/quality."

write_stub "zero-shot-socratic" \
  "On the Helpfulness of a Zero-Shot Socratic Tutor" \
  "10.1007/978-981-97-9255-9_11" \
  "GPT-4 homework tutor using Socratic method; helpfulness 4.0/5, rarely leaks solutions."

write_stub "socratic-hard-problem" \
  "The Pedagogical Hard Problem of Generative AI: Socratic Countermeasures" \
  "10.1080/03057240.2026.2631191" \
  "Argues GenAI makes traditional assessment unreliable; proposes Socratic countermeasures for productive struggle."

echo "=== Download summary ==="
ls -lh "$REF_DIR"
