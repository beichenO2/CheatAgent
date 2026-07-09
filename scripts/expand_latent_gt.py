"""Expand latent GT so dialogue indicators ↔ GT indicators (不多不少).

Per-session: mine user assertions → session['claims_truth'].
User-level latent.claims_truth keeps core TRUTH_VARIANTS values; also stores
union for audit. Existing core values always win on (region, indicator).

Eval should prefer session['claims_truth'] when present.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from market_truth_agent.analysis.ontology import INDICATORS, REGIONS
from market_truth_agent.llm.client import llm_mode, normalize_model, tool_completion
from market_truth_agent.utils.progress import progress

_VALUE_ENUM = [
    "高", "中", "低",
    "积极", "消极", "中性",
    "是", "否",
]


def _valid(indicator: str, value: str) -> bool:
    if indicator == "采购积极性":
        return value in {"积极", "消极", "中性"}
    if indicator == "报价松动":
        return value in {"是", "否"}
    return value in {"高", "中", "低"}


def _tool_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "asserted_slots": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "region": {"type": "string", "enum": list(REGIONS)},
                        "indicator": {"type": "string", "enum": list(INDICATORS)},
                        "value": {"type": "string", "enum": _VALUE_ENUM},
                        "evidence": {"type": "string"},
                    },
                    "required": ["region", "indicator", "value", "evidence"],
                },
            }
        },
        "required": ["asserted_slots"],
    }


def mine_asserted_slots(
    *,
    user_turns: list[str],
    core_gt: list[dict[str, Any]],
    default_region: str,
) -> list[dict[str, Any]]:
    system = """你是 session 级 latent GT 标注器。

任务：阅读**本 session** 客户发言，列出客户**第一手明确断言**的指标（不多不少）。

## 什么算断言
- 客户以自己身份对**自己所在区域**（default_region）行情的直接判断
- 「疏港节奏跟平时差不多/挺稳」→ 疏港量=中；「发运快了」→ 发运=高

## 什么不算断言（一律不建槽，ADR-010 L4）
- 客服诱导/谣言本身不算；客户「不清楚/说不准/那边不了解」不算
- **转述/传闻回声**：客户复述客服或他人的说法（「听说」「据说」「你说的那个」
  「他们那边库存低」「那边跟我们不是一回事」）——即使语气肯定也不算
- **对比他港的带过句**：为了反衬本港而顺嘴提到别的港口，不算对该港的断言
- 跨 region 建槽的唯一条件：客户**以第一手身份**明确断言该港（如「我在青岛也有仓，
  那边港存确实低」）；仅凭比较句/听闻禁止建槽

## value 规范
- 采购积极性：还行/按需/随行就市/中性 → 中性（禁止 value=中）
- 利润「还行/一般」→ 中（禁止 上涨/下跌）

## 其它
- region 默认 default_region
- 核心 GT 供参考：同槽冲突时以客户本 session 最清晰表述为准，但通常应与核心 GT 一致
- 输出前自检（防漏标）：对照指标全表（港存/到港量/疏港量/采购积极性/报价松动/利润/压港/发运）
  逐一确认客户是否有第一手断言；漏标与多标同样是错误

输出 JSON:
{"asserted_slots":[{"region":"青岛港","indicator":"港存","value":"中","evidence":"短句"}]}"""

    dialogue = "\n".join(f"- {t}" for t in user_turns)
    user = f"""default_region: {default_region}
core_gt: {json.dumps(core_gt, ensure_ascii=False)}

本 session 客户发言:
{dialogue}

请输出本 session 的 asserted_slots（对话里断言了哪些就列哪些）。"""

    if llm_mode() == "mock":
        return [
            {
                "region": c["region"],
                "indicator": c["indicator"],
                "value": c["value"],
                "evidence": "mock",
            }
            for c in core_gt
        ]

    payload = tool_completion(
        system,
        user,
        tool_name="emit_asserted_slots",
        tool_description="列出本 session 客户明确断言的指标槽位",
        parameters_schema=_tool_schema(),
        temperature=0.1,
        model=normalize_model(),
    )
    if not payload or not isinstance(payload.get("asserted_slots"), list):
        return []
    # Hearsay-echo markers: a cross-region slot whose evidence reads like
    # relaying someone else's words is not a first-hand assertion (ADR-010 L4).
    hearsay = ("听说", "据说", "你说", "您说", "他们", "那边", "不是一回事", "对上号")
    out: list[dict[str, Any]] = []
    for item in payload["asserted_slots"]:
        if not isinstance(item, dict):
            continue
        region = str(item.get("region", default_region))
        indicator = str(item.get("indicator", ""))
        value = str(item.get("value", "")).strip()
        evidence = str(item.get("evidence", ""))
        if indicator == "采购积极性" and value == "中":
            value = "中性"
        if region not in REGIONS or indicator not in INDICATORS:
            continue
        if not _valid(indicator, value):
            continue
        if region != default_region and any(m in evidence for m in hearsay):
            progress(f"[gt-expand] drop hearsay-echo {region}/{indicator}={value} ({evidence[:40]})")
            continue
        out.append(
            {
                "region": region,
                "indicator": indicator,
                "value": value,
                "market_object": "铁矿石",
                "evidence": evidence,
            }
        )
    return out


def merge_with_core(
    core_gt: list[dict[str, Any]],
    mined: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Core wins on key; append mined-only slots. Always include core slots that
    appear in mined OR keep all core (world truth) — for session GT we want
    dialogue-aligned: use mined if non-empty, but force core values when both exist.
    """
    if not mined:
        return [
            {
                "region": c["region"],
                "indicator": c["indicator"],
                "value": c["value"],
                "market_object": c.get("market_object", "铁矿石"),
            }
            for c in core_gt
        ]
    core_map = {(c["region"], c["indicator"]): c for c in core_gt}
    by_key: dict[tuple[str, str], dict[str, Any]] = {}
    # Start from mined (dialogue-asserted)
    for c in mined:
        key = (c["region"], c["indicator"])
        if key in core_map:
            # Core world-truth wins on value
            src = core_map[key]
            by_key[key] = {
                "region": src["region"],
                "indicator": src["indicator"],
                "value": src["value"],
                "market_object": "铁矿石",
            }
        else:
            by_key[key] = {
                "region": c["region"],
                "indicator": c["indicator"],
                "value": c["value"],
                "market_object": "铁矿石",
            }
    # Ensure core indicators that were discussed stay; if a core indicator was
    # never mined, omit it (不多不少 — not in dialogue → not in session GT).
    # Exception: if mined is only extras and missed core, fall back include core.
    core_keys_in_mined = {k for k in by_key if k in core_map}
    if not core_keys_in_mined:
        for c in core_gt:
            by_key[(c["region"], c["indicator"])] = {
                "region": c["region"],
                "indicator": c["indicator"],
                "value": c["value"],
                "market_object": "铁矿石",
            }
    # Stable: core order first, then extras
    ordered: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for c in core_gt:
        key = (c["region"], c["indicator"])
        if key in by_key:
            ordered.append(by_key[key])
            seen.add(key)
    for key, slot in by_key.items():
        if key not in seen:
            ordered.append(slot)
    return ordered


def expand_user_meta(meta: dict[str, Any]) -> dict[str, Any]:
    persona = meta["persona"]
    # Core = original 3-slot truth (strip previous expands)
    raw = list(meta.get("latent", {}).get("claims_truth", []))
    core_indicators = {"港存", "采购积极性", "报价松动"}
    core_gt = [c for c in raw if c.get("indicator") in core_indicators]
    if len(core_gt) < 3:
        # already expanded mess — take first occurrence per core indicator
        seen: set[str] = set()
        core_gt = []
        for c in raw:
            ind = c.get("indicator")
            if ind in core_indicators and ind not in seen:
                core_gt.append(
                    {
                        "region": c["region"],
                        "indicator": ind,
                        "value": c["value"],
                        "market_object": "铁矿石",
                    }
                )
                seen.add(ind)

    default_region = persona.get("region", "青岛港")
    sessions_out = []
    union: dict[tuple[str, str], dict[str, Any]] = {
        (c["region"], c["indicator"]): {
            "region": c["region"],
            "indicator": c["indicator"],
            "value": c["value"],
            "market_object": "铁矿石",
        }
        for c in core_gt
    }
    audit: list[dict[str, Any]] = []

    for session in meta.get("sessions", []):
        user_turns = [
            t["text"]
            for t in session.get("turns", [])
            if t.get("speaker") == "user" and t.get("text")
        ]
        # beta_v2 world-state datasets carry per-session world truth
        session_core = session.get("world_truth") or core_gt
        mined = mine_asserted_slots(
            user_turns=user_turns,
            core_gt=session_core,
            default_region=default_region,
        )
        session_gt = merge_with_core(session_core, mined)
        sess = dict(session)
        sess["claims_truth"] = session_gt
        sessions_out.append(sess)
        for c in session_gt:
            union[(c["region"], c["indicator"])] = c
        audit.append(
            {
                "session_id": session.get("session_id"),
                "mined": mined,
                "session_gt": session_gt,
            }
        )
        progress(
            f"[gt-expand] {persona.get('user_id')} {session.get('session_id')} "
            f"slots={len(session_gt)} {[c['indicator'] for c in session_gt]}"
        )

    meta = dict(meta)
    latent = dict(meta.get("latent", {}))
    latent["claims_truth"] = list(union.values())  # union audit / multi-session TD
    latent["core_claims_truth"] = core_gt
    latent["gt_expand"] = {"sessions": audit}
    meta["latent"] = latent
    meta["sessions"] = sessions_out
    return meta


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=Path("benchmark/datasets/beta_v1"))
    parser.add_argument("--users", nargs="*", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    users_dir = args.dataset / "users"
    targets = sorted(p.name for p in users_dir.iterdir() if p.is_dir())
    if args.users:
        targets = [u for u in targets if u in set(args.users)]

    summary = []
    for uid in targets:
        path = users_dir / uid / "meta.json"
        meta = json.loads(path.read_text(encoding="utf-8"))
        progress(f"[gt-expand] === {uid} ===")
        expanded = expand_user_meta(meta)
        row = {
            "user_id": uid,
            "core": expanded["latent"]["core_claims_truth"],
            "union": expanded["latent"]["claims_truth"],
            "sessions": [
                {
                    "session_id": s["session_id"],
                    "n": len(s.get("claims_truth", [])),
                    "indicators": [c["indicator"] for c in s.get("claims_truth", [])],
                }
                for s in expanded["sessions"]
            ],
        }
        summary.append(row)
        if not args.dry_run:
            path.write_text(
                json.dumps(expanded, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

    out = args.dataset / "gt_expand_summary.json"
    if not args.dry_run:
        out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
