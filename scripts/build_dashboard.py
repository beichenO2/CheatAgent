#!/usr/bin/env python3
"""Build the paper-style static dashboard (ADR-011).

Reads eval checkpoints (works mid-run) + dataset meta + optional cross-user TD
report, computes statistics in Python (mean±std, bootstrap 95% CI, Pearson,
least-squares fit), and emits a single self-contained HTML file with embedded
JSON + ECharts (CDN).

Usage:
  python scripts/build_dashboard.py --preset beta_v1
  # output: benchmark/reports/<preset>/dashboard.html
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from market_truth_agent.agents.eval.claim_metrics import pearson_correlation

FUSION_MODES = ("llm", "voting", "last_wins")
CORE3 = ("港存", "采购积极性", "报价松动")


# ─── stats helpers ──────────────────────────────────────────────────────────

def mean(xs: list[float]) -> float | None:
    return sum(xs) / len(xs) if xs else None


def std(xs: list[float]) -> float | None:
    if len(xs) < 2:
        return 0.0 if xs else None
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def bootstrap_ci(xs: list[float], n_boot: int = 1000, alpha: float = 0.05,
                 seed: int = 42) -> tuple[float, float] | None:
    if not xs:
        return None
    rng = random.Random(seed)
    means = sorted(
        sum(rng.choice(xs) for _ in range(len(xs))) / len(xs) for _ in range(n_boot)
    )
    lo = means[int((alpha / 2) * n_boot)]
    hi = means[min(int((1 - alpha / 2) * n_boot), n_boot - 1)]
    return (lo, hi)


def least_squares(xs: list[float], ys: list[float]) -> tuple[float, float] | None:
    n = len(xs)
    if n < 2:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return None
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
    return slope, my - slope * mx


# ─── data loading ───────────────────────────────────────────────────────────

def load_data(preset: str) -> dict[str, Any]:
    ckpt_dir = ROOT / "benchmark/reports" / preset / "checkpoints"
    dataset_dir = ROOT / "benchmark/datasets" / preset

    personas: dict[str, dict[str, Any]] = {}
    session_gt: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for meta_path in sorted(dataset_dir.glob("users/*/meta.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        p = meta["persona"]
        personas[p["user_id"]] = p
        for s in meta.get("sessions", []):
            gt = s.get("claims_truth") or meta.get("latent", {}).get("claims_truth", [])
            session_gt[(p["user_id"], s["session_id"])] = gt

    rows: list[dict[str, Any]] = []
    for ckpt in sorted(ckpt_dir.glob("*_eval.json")):
        data = json.loads(ckpt.read_text(encoding="utf-8"))
        uid = data.get("user_row", {}).get("user_id") or ckpt.name.split("_")[0]
        honesty = data.get("user_row", {}).get("honesty_gt")
        for r in data.get("session_metric_rows", []):
            fusion = r.get("fusion_ablation") or {}
            row = {
                "user_id": uid,
                "honesty": honesty,
                "region": personas.get(uid, {}).get("region", "?"),
                "session_id": r.get("session_id"),
                "claim_count": r.get("claim_count", 0),
                "mean_deception": (r.get("recon") or {}).get("mean_deception"),
                "veracity_acc": (r.get("veracity") or {}).get("bucket_veracity_accuracy"),
                "veracity_scope": (r.get("veracity") or {}).get("veracity_scope"),
                "escalation_rate": (r.get("escalation") or {}).get("escalation_rate"),
                "external": (r.get("external") or {}).get("external_consistency_mean"),
                "modes": {},
                "fused_llm": (fusion.get("llm") or {}).get("fused_slots") or {},
            }
            for mode in FUSION_MODES:
                m = fusion.get(mode) or {}
                if m:
                    row["modes"][mode] = {
                        k: m.get(k) for k in ("f1", "recall", "precision", "tp", "fp", "fn")
                    }
            rows.append(row)

    cross_td_path = ROOT / "benchmark/reports" / preset / "cross_user_td.json"
    cross_td = (
        json.loads(cross_td_path.read_text(encoding="utf-8"))
        if cross_td_path.exists() else None
    )
    return {
        "rows": rows,
        "personas": personas,
        "session_gt": session_gt,
        "cross_td": cross_td,
        "n_users_total": len(personas),
    }


# ─── aggregation ────────────────────────────────────────────────────────────

def aggregate(data: dict[str, Any]) -> dict[str, Any]:
    rows = data["rows"]
    users_evaluated = sorted({r["user_id"] for r in rows})

    ablation = {}
    for mode in FUSION_MODES:
        per_metric = {}
        for metric in ("f1", "recall", "precision"):
            xs = [r["modes"][mode][metric] for r in rows
                  if mode in r["modes"] and r["modes"][mode].get(metric) is not None]
            ci = bootstrap_ci(xs)
            per_metric[metric] = {
                "mean": mean(xs), "std": std(xs),
                "ci_lo": ci[0] if ci else None, "ci_hi": ci[1] if ci else None,
                "n": len(xs),
            }
        ablation[mode] = per_metric

    # user-level aggregates
    user_rows = []
    for uid in users_evaluated:
        sub = [r for r in rows if r["user_id"] == uid]
        f1s = [r["modes"]["llm"]["f1"] for r in sub if "llm" in r["modes"]]
        decs = [r["mean_deception"] for r in sub if r["mean_deception"] is not None]
        vers = [r["veracity_acc"] for r in sub if r["veracity_acc"] is not None]
        user_rows.append({
            "user_id": uid,
            "honesty": sub[0]["honesty"],
            "region": sub[0]["region"],
            "n_sessions": len(sub),
            "f1_mean": mean(f1s),
            "deception_mean": mean(decs),
            "veracity_mean": mean(vers),
            "claims": sum(r["claim_count"] for r in sub),
        })

    # deception vs honesty (user level)
    pairs = [(u["honesty"], u["deception_mean"]) for u in user_rows
             if u["honesty"] is not None and u["deception_mean"] is not None]
    dec_scatter = [{"x": h, "y": d, "uid": u["user_id"]}
                   for (h, d), u in zip(pairs, [u for u in user_rows
                   if u["honesty"] is not None and u["deception_mean"] is not None])]
    dec_r = pearson_correlation([p[0] for p in pairs], [p[1] for p in pairs]) if len(pairs) >= 2 else None
    dec_fit = least_squares([p[0] for p in pairs], [p[1] for p in pairs])

    # reliability vs honesty (cross-user TD, if present)
    rel_scatter, rel_r, rel_fit, rel_note = [], None, None, None
    if data["cross_td"]:
        td = data["cross_td"]
        rel_rows = td.get("reliability", [])
        rel_scatter = [{"x": r["honesty_gt"], "y": r["reliability_est"], "uid": r["user_id"]}
                       for r in rel_rows]
        rp = td.get("reliability_pearson") or {}
        rel_r = rp.get("pearson_r")
        xs = [r["x"] for r in rel_scatter]; ys = [r["y"] for r in rel_scatter]
        rel_fit = least_squares(xs, ys)
        rel_note = td.get("note")

    # per-indicator difficulty from fused(llm) vs session GT
    ind_stats: dict[str, dict[str, int]] = {}
    for r in rows:
        gt = data["session_gt"].get((r["user_id"], r["session_id"]), [])
        gt_map = {(c["region"], c["indicator"]): c["value"] for c in gt}
        pred_map = {}
        for key, slot in (r["fused_llm"] or {}).items():
            region, _, indicator = key.partition("/")
            pred_map[(region, indicator)] = slot.get("value")
        for key in set(gt_map) | set(pred_map):
            ind = key[1]
            st = ind_stats.setdefault(ind, {"tp": 0, "fp": 0, "fn": 0})
            g, p = gt_map.get(key), pred_map.get(key)
            if g is not None and p is not None:
                if g == p:
                    st["tp"] += 1
                else:
                    st["fp"] += 1; st["fn"] += 1
            elif g is not None:
                st["fn"] += 1
            else:
                st["fp"] += 1
    indicators = []
    for ind, st in sorted(ind_stats.items()):
        tp, fp, fn = st["tp"], st["fp"], st["fn"]
        indicators.append({
            "indicator": ind, "core": ind in CORE3,
            "recall": tp / (tp + fn) if tp + fn else None,
            "precision": tp / (tp + fp) if tp + fp else None,
            "support": tp + fn,
        })

    f1_llm = [r["modes"]["llm"]["f1"] for r in rows if "llm" in r["modes"]]
    ver = [r["veracity_acc"] for r in rows if r["veracity_acc"] is not None]
    esc = [r["escalation_rate"] for r in rows if r["escalation_rate"] is not None]

    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "n_users_evaluated": len(users_evaluated),
        "n_users_total": data["n_users_total"],
        "n_sessions": len(rows),
        "n_claims": sum(r["claim_count"] for r in rows),
        "kpi": {
            "f1": {"mean": mean(f1_llm), "std": std(f1_llm), "ci": bootstrap_ci(f1_llm)},
            "veracity": {"mean": mean(ver), "std": std(ver)},
            "escalation": {"mean": mean(esc)},
        },
        "ablation": ablation,
        "user_rows": user_rows,
        "dec_scatter": {"points": dec_scatter, "r": dec_r, "n": len(pairs), "fit": dec_fit},
        "rel_scatter": {"points": rel_scatter, "r": rel_r, "n": len(rel_scatter),
                        "fit": rel_fit, "note": rel_note},
        "indicators": indicators,
        "f1_dist": f1_llm,
    }


# ─── HTML ───────────────────────────────────────────────────────────────────

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<title>MarketTruthAgent — __PRESET__ 评测报告</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<style>
  :root { --ink:#1a1a1a; --muted:#666; --line:#d8d4cc; --accent:#8b1a1a; --bg:#faf9f6; }
  * { box-sizing:border-box; }
  body { font-family:"Songti SC","SimSun",Georgia,serif; color:var(--ink);
         background:var(--bg); margin:0; padding:40px 24px; }
  .paper { max-width:1080px; margin:0 auto; background:#fff; border:1px solid var(--line);
           padding:56px 64px; box-shadow:0 1px 4px rgba(0,0,0,.06); }
  h1 { font-size:26px; margin:0 0 4px; letter-spacing:.5px; }
  .subtitle { color:var(--muted); font-size:14px; margin-bottom:6px; }
  .runstate { font-size:13px; color:var(--accent); margin-bottom:28px; }
  h2 { font-size:19px; margin:44px 0 12px; border-bottom:1px solid var(--line); padding-bottom:6px; }
  p.note { font-size:13px; color:var(--muted); line-height:1.7; margin:6px 0 14px; }
  .kpis { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin:18px 0; }
  .kpi { border:1px solid var(--line); padding:14px 16px; }
  .kpi .v { font-size:22px; font-family:Georgia,serif; }
  .kpi .l { font-size:12px; color:var(--muted); margin-top:2px; }
  .kpi .s { font-size:11px; color:var(--muted); }
  table { border-collapse:collapse; width:100%; font-size:13px; margin:10px 0 6px; }
  th,td { border:1px solid var(--line); padding:7px 10px; text-align:center; }
  th { background:#f4f2ed; font-weight:600; }
  td.l,th.l { text-align:left; }
  .best { font-weight:700; }
  .caption { font-size:12.5px; color:var(--muted); margin:6px 0 0; line-height:1.6; }
  .caption b { color:var(--ink); }
  .chart { width:100%; height:360px; margin-top:14px; }
  .chart.tall { height:420px; }
  .placeholder { border:1px dashed var(--line); color:var(--muted); font-size:13px;
                 padding:32px; text-align:center; margin-top:14px; }
  footer { margin-top:52px; font-size:12px; color:var(--muted); line-height:1.8;
           border-top:1px solid var(--line); padding-top:14px; }
  code { font-family:Menlo,monospace; font-size:12px; background:#f4f2ed; padding:1px 5px; }
</style>
</head>
<body>
<div class="paper">
  <h1>MarketTruthAgent 评测报告</h1>
  <div class="subtitle">数据集 __PRESET__ · 30 用户 × 5 session × 20 轮 · 分析链路 ReCon → Normalize → Fusion → Truth Discovery</div>
  <div class="runstate" id="runstate"></div>

  <h2>1 总览</h2>
  <div class="kpis" id="kpis"></div>
  <p class="note" id="kpi-note"></p>

  <h2>2 融合层消融（表 1 · 图 1）</h2>
  <p class="note">同一批逐轮 Normalize claim，分别经 LLM 语义融合 / 置信度加权投票 / last-wins
     聚合为最终槽位后与 session GT 对比。session 级 slot F1/recall/precision 的
     mean ± std，方括号为 bootstrap 95% CI（n=1000）。</p>
  <div id="tbl-ablation"></div>
  <p class="caption"><b>表 1</b>：融合模式消融。GT = 对话对齐 session GT（扩标口径见 ADR-010）；最优值加粗。</p>
  <div class="chart" id="chart-ablation"></div>
  <p class="caption"><b>图 1</b>:三种融合模式的 slot 指标（误差条 = 95% CI）。对应判例 TC-07/TC-08：语义等价与追问澄清需读全局，逐轮投票产生分裂票。</p>

  <h2>3 欺骗信号标定（图 2）</h2>
  <div class="chart" id="chart-dec"></div>
  <p class="caption" id="cap-dec"></p>

  <h2>4 来源可靠度标定（图 3）</h2>
  <div id="rel-holder"></div>
  <p class="caption" id="cap-rel"></p>

  <h2>5 指标难度（图 4）</h2>
  <div class="chart" id="chart-ind"></div>
  <p class="caption"><b>图 4</b>：per-indicator recall / precision（fusion=llm）。●=核心三槽（honesty 约束的世界真值），○=扩标指标（对话断言口径）。</p>

  <h2>6 Session F1 分布（图 5）</h2>
  <div class="chart" id="chart-dist"></div>
  <p class="caption"><b>图 5</b>：session 级 slot F1（fusion=llm）直方图。</p>

  <h2>7 用户明细（表 2）</h2>
  <div id="tbl-users" style="max-height:420px;overflow:auto"></div>
  <p class="caption"><b>表 2</b>：用户级汇总。reliability 列在 cross-user TD 报告存在时填充。</p>

  <h2>8 指标定义（表 3）</h2>
  <table>
    <tr><th class="l">指标</th><th class="l">定义</th><th class="l">GT 来源 / 口径</th></tr>
    <tr><td class="l">slot F1 / recall / precision</td><td class="l">融合后 (region, indicator, value) 槽位与 session GT 的集合匹配</td><td class="l">对话对齐 session GT（`claims_truth`，扩标：核心值以 latent 为准）</td></tr>
    <tr><td class="l">bucket_veracity_accuracy</td><td class="l">1 − TD bucket 推断错误率</td><td class="l">仅核心三槽 × persona region（世界真值；ADR-010 L3）</td></tr>
    <tr><td class="l">mean_deception</td><td class="l">ReCon 每 user turn 策略性风格分均值</td><td class="l">无 GT；与 honesty 求相关（期望负）</td></tr>
    <tr><td class="l">reliability_est</td><td class="l">Beta(2,2) 后验均值；仅多源桶更新</td><td class="l">cross-user TD（ADR-010 L1）；对 honesty 求 Pearson</td></tr>
    <tr><td class="l">escalation_rate</td><td class="l">触发人工升级的 claim 占比</td><td class="l">策略层，无 GT</td></tr>
  </table>
  <p class="caption"><b>表 3</b>：口径备忘详见 <code>decisions/010</code>；可视化规范见 <code>decisions/011</code>。</p>

  <footer>
    复现：<code>python scripts/run_benchmark_pipeline.py --preset __PRESET__ --phase evaluate --resume</code>
    → <code>python scripts/cross_user_td.py --preset __PRESET__</code>
    → <code>python scripts/build_dashboard.py --preset __PRESET__</code><br>
    生成时间 __GENERATED__ · MarketTruthAgent（CheatAgent）· ADR-001/005/009/010/011
  </footer>
</div>

<script>
const D = __DATA__;
const fmt = (x, d=3) => x == null ? "—" : x.toFixed(d);
const pct = x => x == null ? "—" : (100*x).toFixed(1) + "%";

// run state
document.getElementById("runstate").textContent =
  `已评测 ${D.n_users_evaluated}/${D.n_users_total} 用户 · ${D.n_sessions} session · ${D.n_claims} claims` +
  (D.n_users_evaluated < D.n_users_total ? " ·（评测仍在进行，本页为阶段性快照）" : "");

// KPIs
const k = D.kpi;
document.getElementById("kpis").innerHTML = [
  {v: fmt(k.f1.mean), s: k.f1.ci ? `±${fmt(k.f1.std,2)} · CI [${fmt(k.f1.ci[0])}, ${fmt(k.f1.ci[1])}]` : "", l: "slot F1（fusion=llm）"},
  {v: fmt(k.veracity.mean), s: k.veracity.std!=null?`±${fmt(k.veracity.std,2)}`:"", l: "veracity（核心三槽）"},
  {v: `${D.n_sessions}`, s: `${D.n_users_evaluated} 用户`, l: "session 数"},
  {v: `${D.n_claims}`, s: pct(k.escalation.mean) + " escalation", l: "claim 总数"},
].map(x=>`<div class="kpi"><div class="v">${x.v}</div><div class="s">${x.s||"&nbsp;"}</div><div class="l">${x.l}</div></div>`).join("");
document.getElementById("kpi-note").textContent =
  "F1 为 session 级均值；CI 为 session 重采样 bootstrap 95% 区间。";

// Table 1: ablation
const MODES = ["llm","voting","last_wins"], MNAME = {llm:"LLM 语义融合", voting:"加权投票", last_wins:"last-wins"};
const METS = ["f1","recall","precision"];
let best = {};
METS.forEach(m => { best[m] = Math.max(...MODES.map(mo => (D.ablation[mo]?.[m]?.mean) ?? -1)); });
document.getElementById("tbl-ablation").innerHTML = "<table><tr><th class='l'>融合模式</th>" +
  METS.map(m=>`<th>${m} (mean±std [95% CI])</th>`).join("") + "<th>n</th></tr>" +
  MODES.map(mo => {
    const a = D.ablation[mo] || {};
    return `<tr><td class='l'>${MNAME[mo]}</td>` + METS.map(m => {
      const s = a[m] || {};
      const cls = s.mean != null && Math.abs(s.mean - best[m]) < 1e-9 ? "best" : "";
      const ci = s.ci_lo != null ? ` [${fmt(s.ci_lo)}, ${fmt(s.ci_hi)}]` : "";
      return `<td class="${cls}">${fmt(s.mean)} ± ${fmt(s.std,2)}${ci}</td>`;
    }).join("") + `<td>${(a.f1||{}).n ?? "—"}</td></tr>`;
  }).join("") + "</table>";

// Figure 1: grouped bars with CI error bars
(function(){
  const el = document.getElementById("chart-ablation");
  const chart = echarts.init(el);
  const series = [];
  MODES.forEach((mo, i) => {
    series.push({
      name: MNAME[mo], type: "bar", barGap: "10%",
      data: METS.map(m => D.ablation[mo]?.[m]?.mean ?? 0),
      itemStyle: {color: ["#8b1a1a","#4a6741","#7d7461"][i]},
    });
    series.push({
      name: MNAME[mo]+"_err", type: "custom", tooltip: {show:false}, silent:true,
      renderItem: (params, api) => {
        const x = api.coord([api.value(0), 0])[0] , lo = api.coord([0, api.value(1)])[1],
              hi = api.coord([0, api.value(2)])[1];
        const off = (i-1) * api.size([1,0])[0] * 0.30 * 0.9;
        return {type:"group", children:[
          {type:"line", shape:{x1:x+off, y1:lo, x2:x+off, y2:hi}, style:{stroke:"#333",lineWidth:1}},
          {type:"line", shape:{x1:x+off-4, y1:lo, x2:x+off+4, y2:lo}, style:{stroke:"#333",lineWidth:1}},
          {type:"line", shape:{x1:x+off-4, y1:hi, x2:x+off+4, y2:hi}, style:{stroke:"#333",lineWidth:1}},
        ]};
      },
      data: METS.map((m, mi) => [mi, D.ablation[mo]?.[m]?.ci_lo ?? 0, D.ablation[mo]?.[m]?.ci_hi ?? 0]),
      z: 10,
    });
  });
  chart.setOption({
    legend: {data: MODES.map(m=>MNAME[m]), top: 0, textStyle:{fontSize:12}},
    grid: {left:48, right:16, top:36, bottom:28},
    xAxis: {type:"category", data:["F1","recall","precision"], axisLabel:{fontSize:12}},
    yAxis: {type:"value", min:0, max:1},
    series, tooltip:{trigger:"axis"},
  });
})();

// scatter builder
function scatterChart(elId, pts, fit, xlabel, ylabel, color){
  const el = document.getElementById(elId);
  const chart = echarts.init(el);
  const series = [{
    type:"scatter", symbolSize:9, itemStyle:{color, opacity:.85},
    data: pts.map(p=>[p.x,p.y]),
    label:{show:false},
  }];
  if (fit && pts.length >= 2){
    const xs = pts.map(p=>p.x), x0 = Math.min(...xs), x1 = Math.max(...xs);
    series.push({type:"line", showSymbol:false, lineStyle:{color:"#333",width:1,type:"dashed"},
      data:[[x0, fit[0]*x0+fit[1]],[x1, fit[0]*x1+fit[1]]], silent:true});
  }
  chart.setOption({
    grid:{left:56,right:20,top:20,bottom:44},
    xAxis:{name:xlabel, nameLocation:"middle", nameGap:28, min:0, max:1, type:"value"},
    yAxis:{name:ylabel, nameLocation:"middle", nameGap:38, type:"value"},
    tooltip:{formatter: p => { const q = pts[p.dataIndex]; return q ? `${q.uid}<br>${xlabel}=${q.x}<br>${ylabel}=${fmt(q.y)}` : ""; }},
    series,
  });
}

// Figure 2: deception vs honesty
scatterChart("chart-dec", D.dec_scatter.points, D.dec_scatter.fit,
             "honesty (GT)", "mean deception (ReCon)", "#8b1a1a");
document.getElementById("cap-dec").innerHTML =
  `<b>图 2</b>：ReCon 策略性风格分 vs honesty，用户级均值。Pearson r = ${fmt(D.dec_scatter.r,3)} (n=${D.dec_scatter.n})，期望负相关。注意 deception 测的是风格而非实锤谎言（CheatAgent.md §五 机理确认）。`;

// Figure 3: reliability vs honesty
if (D.rel_scatter.points.length){
  document.getElementById("rel-holder").innerHTML = '<div class="chart" id="chart-rel"></div>';
  scatterChart("chart-rel", D.rel_scatter.points, D.rel_scatter.fit,
               "honesty (GT)", "reliability posterior", "#4a6741");
  document.getElementById("cap-rel").innerHTML =
    `<b>图 3</b>：cross-user TD Beta 后验 vs honesty。Pearson r = ${fmt(D.rel_scatter.r,3)} (n=${D.rel_scatter.n})。` +
    (D.rel_scatter.note ? ` 备注：${D.rel_scatter.note}` : "");
} else {
  document.getElementById("rel-holder").innerHTML =
    '<div class="placeholder">cross-user TD 报告未生成 — 全量 eval 完成后运行 <code>python scripts/cross_user_td.py</code>。单 session 单源不更新可靠度（Beta 先验守卫），故该图必须来自跨用户阶段。</div>';
  document.getElementById("cap-rel").innerHTML =
    `<b>图 3</b>（待数据）：来源可靠度标定。beta_v1 世界态为按用户独立（诊断用），干净标定见 beta_v2（ADR-010 L2）。`;
}

// Figure 4: indicator difficulty
(function(){
  const chart = echarts.init(document.getElementById("chart-ind"));
  const inds = D.indicators;
  chart.setOption({
    legend:{top:0},
    grid:{left:56,right:16,top:32,bottom:40},
    xAxis:{type:"category", data:inds.map(i=>(i.core?"● ":"○ ")+i.indicator), axisLabel:{fontSize:12,interval:0,rotate:20}},
    yAxis:{type:"value",min:0,max:1},
    series:[
      {name:"recall",type:"bar",data:inds.map(i=>i.recall),itemStyle:{color:"#8b1a1a"}},
      {name:"precision",type:"bar",data:inds.map(i=>i.precision),itemStyle:{color:"#7d7461"}},
    ],
    tooltip:{trigger:"axis", formatter: ps => {
      const i = inds[ps[0].dataIndex];
      return `${i.indicator}（support=${i.support}）<br>recall=${fmt(i.recall)}<br>precision=${fmt(i.precision)}`;
    }},
  });
})();

// Figure 5: F1 histogram
(function(){
  const bins = Array.from({length:10},(_,i)=>({lo:i/10, hi:(i+1)/10, n:0}));
  D.f1_dist.forEach(v => { const b = Math.min(Math.floor(v*10), 9); bins[b].n++; });
  const chart = echarts.init(document.getElementById("chart-dist"));
  chart.setOption({
    grid:{left:48,right:16,top:20,bottom:40},
    xAxis:{type:"category", data:bins.map(b=>`${b.lo.toFixed(1)}–${b.hi.toFixed(1)}`), axisLabel:{fontSize:11}},
    yAxis:{type:"value", name:"sessions"},
    series:[{type:"bar", data:bins.map(b=>b.n), itemStyle:{color:"#4a6741"}, barWidth:"70%"}],
    tooltip:{},
  });
})();

// Table 2: users
(function(){
  const rel = {};
  (D.rel_scatter.points||[]).forEach(p => rel[p.uid] = p.y);
  document.getElementById("tbl-users").innerHTML = "<table><tr>" +
    "<th>用户</th><th>region</th><th>honesty</th><th>sessions</th><th>F1(llm)</th><th>deception</th><th>veracity</th><th>reliability</th><th>claims</th></tr>" +
    D.user_rows.map(u=>`<tr><td>${u.user_id}</td><td>${u.region}</td><td>${fmt(u.honesty,2)}</td>` +
      `<td>${u.n_sessions}</td><td>${fmt(u.f1_mean)}</td><td>${fmt(u.deception_mean)}</td>` +
      `<td>${fmt(u.veracity_mean)}</td><td>${rel[u.user_id]!=null?fmt(rel[u.user_id]):"—"}</td><td>${u.claims}</td></tr>`).join("") +
    "</table>";
})();
</script>
</body>
</html>
"""


def build(preset: str) -> Path:
    data = load_data(preset)
    agg = aggregate(data)
    html = (
        HTML_TEMPLATE
        .replace("__PRESET__", preset)
        .replace("__GENERATED__", agg["generated_at"])
        .replace("__DATA__", json.dumps(agg, ensure_ascii=False))
    )
    out = ROOT / "benchmark/reports" / preset / "dashboard.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"[dashboard] {agg['n_users_evaluated']}/{agg['n_users_total']} users, "
          f"{agg['n_sessions']} sessions → {out}")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", default="beta_v1")
    args = parser.parse_args()
    build(args.preset)


if __name__ == "__main__":
    main()
