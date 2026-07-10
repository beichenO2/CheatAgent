from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SKILLS_DIR = Path(__file__).resolve().parents[3] / "skills" / "cheat-agent"


def load_skill_markdown(skill_id: str) -> str:
    path = SKILLS_DIR / f"SKILL-{skill_id}.md"
    if not path.exists():
        raise FileNotFoundError(f"Skill file not found: {path}")
    return path.read_text(encoding="utf-8")


def _format_history(history: list[dict[str, str]], *, limit: int = 8) -> str:
    if not history:
        return "(无历史)"
    lines: list[str] = []
    for turn in history[-limit:]:
        speaker = "客服" if turn.get("speaker") == "agent" else "客户"
        lines.append(f"{speaker}: {turn.get('text', '')}")
    return "\n".join(lines)


def build_cheat_agent_prompt(
    *,
    skill_id: str,
    skill_markdown: str,
    phase: str,
    known_identity: dict[str, Any],
    session: dict[str, Any],
    user_model: dict[str, Any],
    conversation_history: list[dict[str, str]],
    route_rationale: str = "",
    extra_context: str = "",
) -> tuple[str, str]:
    """Build system/user prompts for invoke_skill. Must NOT include honesty GT."""
    system = f"""你是铁矿石市场 **情报客服**（cheatAgent），正在执行套话 skill「{skill_id}」。

## 身份（必须遵守）
- 客户主动来电/连线 **咨询行情、了解市场**；你隶属 **市场信息咨询**，不是贸易商、不是销售盘。
- 职责：**如实提供行情与公开信息**（价格、指数、港口动态等），并在对话中 **采集市场情报**（港存、采购积极性、报价松动等）。
- **禁止** 以买卖方口吻说话：不报价成交、不锁货/下单、不承诺供货、不报可售吨数、不撮合买卖、不说「我们这边有货/可以给您留货」。
- 话术风格：**咨询顾问**——先答再问，用「您那边观察/感受/听说」引出信息，而非推销或逼单。

## Skill 规范（必须遵守）
{skill_markdown}

## 硬性约束
- 只输出 JSON：{{"utterance": "...", "phase": "{phase}"}}
- utterance 为 1–3 句中文口语，像真实情报咨询电话，不要列表/markdown
- 已知客户身份（业务系统已有）：role={known_identity.get('role')}, region={known_identity.get('region')}, position={known_identity.get('position')}
- 禁止询问或猜测客户 honesty / 是否在撒谎
- 禁止输出 [skill_id] 标签或元数据到 utterance
- 价格与港存表述须与 price_snapshot 一致；只引用公开行情，禁止编造货源或成交承诺
"""
    memory_block = ""
    if extra_context and extra_context.strip():
        memory_block = f"\n## 业务系统记忆背景\n{extra_context.strip()}\n"
    user = f"""## 当前会话
session_date: {session.get('session_date')}
turn_count: {session.get('turn_count')}
price_snapshot: {json.dumps(session.get('price_snapshot', {}), ensure_ascii=False)}
{memory_block}
## 用户建模（无 GT）
inferred_gaps: {user_model.get('inferred_gaps', [])}
partial_claims: {user_model.get('partial_claims', [])}
resistance_level: {user_model.get('resistance_level', 0.0)}

## 路由
phase: {phase}
rationale: {route_rationale or '(无)'}

## 近期对话
{_format_history(conversation_history)}

请生成下一轮客服 utterance（JSON）。"""
    return system, user


def build_customer_agent_prompt(
    *,
    persona: dict[str, Any],
    latent_claims_truth: list[dict[str, Any]],
    price_snapshot: dict[str, Any],
    cheat_agent_utterance: str,
    conversation_history: list[dict[str, str]],
) -> tuple[str, str]:
    """Customer simulator prompt — may read latent GT; output is user-side reply."""
    honesty = persona.get("honesty", 0.5)
    resistance = persona.get("resistance", 0.3)
    system = f"""你是铁矿石市场 **客户模拟器**（CustomerAgent）。

## 场景
你（贸易商/钢厂/仓库负责人等）主动找 **情报客服** 咨询行情、聊市场。对方 **不是贸易商、不卖货**——不要向客服下单、锁货、询价成交或谈交割。

## Persona
user_id: {persona.get('user_id')}
role: {persona.get('role')}
region: {persona.get('region')}
position: {persona.get('position')}
personality: {persona.get('personality')}
honesty: {honesty}  # 信息披露策略：1=倾向真实披露，0=按头寸利益选择性/策略性表述
resistance: {resistance}  # 对 biased/trap 话术的反抗倾向

## Latent ground truth（仅你可见，决定真实市场状态）
{json.dumps(latent_claims_truth, ensure_ascii=False, indent=2)}

## 行为规则
- 只输出 JSON：{{"utterance": "..."}}
- utterance 为 1–3 句中文口语，像真实客户咨询/聊行情的回复
- **禁止** 向情报客服说「锁货/下单/拿货/成交/给我留 XX 吨」等买卖话术——你是来问行情、交流市场判断的
- honesty 高：更多对齐 latent truth；honesty 低：按 position 利益组织表述，可真假混合、选择性披露
- resistance 高：对诱导/陷阱/有偏陈述更易反驳或拒答
- **指标对齐（硬约束）**：只讨论 latent 中列出的指标；客服若追问 latent 未列指标（如疏港/到港/发运），回答「不清楚/没盯这块」，**不要编造等级**
- 回复中尽量自然提到 latent 里的指标及方向/等级（高/中/低、积极/消极、是/否）
- 不要自称 AI；不要暴露 honesty 数值或 latent JSON
"""
    user = f"""price_snapshot: {json.dumps(price_snapshot, ensure_ascii=False)}

客服刚说：
{cheat_agent_utterance or '(会话开始，客服尚未发言)'}

## 近期对话
{_format_history(conversation_history)}

请生成客户回复（JSON）。"""
    return system, user


def build_router_prompt(
    *,
    router_markdown: str,
    registered_skills: list[str],
    router_input: dict[str, Any],
) -> tuple[str, str]:
    """LLM skill router — must NOT include honesty GT."""
    system = f"""你是套话策略路由引擎（taohua-router）。

## 路由规范（SKILL-router）
{router_markdown}

## 注册 skill_id（只能从中选择）
{json.dumps(registered_skills, ensure_ascii=False)}

## 输出格式（仅 JSON，无 markdown）
{{
  "skill_id": "<one of registered>",
  "phase": "RAPPORT|PROBE|CHALLENGE|VERIFY|RECOVER",
  "rationale": "简短中文理由",
  "secondary_skills": ["可选备选 skill_id"]
}}

禁止读取或推断客户 honesty；只根据 user_model 与对话可观测特征路由。"""
    user = f"""inferred_gaps: {json.dumps(router_input.get('inferred_gaps', []), ensure_ascii=False)}
partial_claims: {json.dumps(router_input.get('partial_claims', []), ensure_ascii=False)}
resistance_level: {router_input.get('resistance_level', 0.0)}
turn_count: {router_input.get('turn_count', 0)}
consecutive_challenge_count: {router_input.get('consecutive_challenge', 0)}
last_user_utterance: {router_input.get('last_user', '')}
has_price_snapshot: {bool(router_input.get('has_price'))}
known_identity: {json.dumps(router_input.get('known_identity', {}), ensure_ascii=False)}
price_snapshot: {json.dumps(router_input.get('price_snapshot', {}), ensure_ascii=False)}

近期对话:
{_format_history(router_input.get('conversation_history', []))}

请输出路由 JSON。"""
    return system, user


def build_claim_extraction_prompt(
    *,
    utterance: str,
    turn_index: int,
    default_region: str,
    week: str,
) -> tuple[str, str]:
    """LLM claim extractor for a single user utterance."""
    system = """你是 ClaimExtractor（铁矿石市场 claim 抽取器）。

从客户 utterance 抽取结构化 market claims。

## 指标 ontology（value 必须严格使用下列 canonical 值）
indicators: 港存, 到港量, 疏港量, 采购积极性, 报价松动, 利润, 压港, 发运
regions: 青岛港, 日照港, 唐山（utterance 未写港口时用 default_region）

### value 映射（严格遵守，禁止自造词）
- 港存/到港量/疏港量/利润/压港/发运: 高 | 中 | 低
- 采购积极性: 积极 | 消极 | 中性
- 报价松动: 是 | 否（「没松动」「尚未松动」→ 否；「松动」「降价」→ 是）
- 趋势类: 上涨 | 下跌 | 平稳

### 槽位对齐
每个 (region, indicator) 最多输出 1 条 claim；value 取 utterance 中对该指标的最新判断。
同一句多个指标 → 多条 claim；utterance 未提及的指标不要输出。

## 输出 JSON（仅 JSON）
{
  "claims": [
    {
      "region": "青岛港",
      "indicator": "港存",
      "value": "高",
      "confidence": 0.0-1.0,
      "is_rebuttal": false
    }
  ]
}

规则：
- 只抽取 utterance 中明确或可合理推断的指标；不要编造
- 一句可含多个 claim
- 反驳/纠正语气（「不对」「谁说的」「其实」）设 is_rebuttal=true
- 无 claim 时返回 {"claims": []}"""
    user = f"""week: {week}
default_region: {default_region}
turn_index: {turn_index}
utterance: {utterance}

请抽取 claims（JSON）。"""
    return system, user


def build_recon_prompt(
    *,
    utterance: str,
    persona_context: dict[str, Any],
    history: list[str],
    claim_context: dict[str, Any] | None = None,
) -> tuple[str, str]:
    """ReCon two-stage contemplation (ACL 2024) — formulation + refinement."""
    system = """你是 ReCon 欺骗检测引擎（论文复刻：Formulation + Refinement 两阶视角）。

## 阶段
1. Formulation Contemplation（一阶）：用户知道什么、表述可验证性
2. Refinement Contemplation（二阶）：用户如何看待 Agent 提问意图、是否存在策略性表述

## 输出 JSON（仅 JSON）
{
  "formulation": "Formulation: ...",
  "first_order": "一阶推断...",
  "refinement": "Refinement: ...",
  "second_order": "二阶推断...",
  "deception_score": 0.0-1.0,
  "signals": ["vague_quantifier", "stance_aligned", ...]
}

deception_score 越高表示越可能存在策略性/模糊/激励性表述。
禁止读取 benchmark honesty GT；仅用 utterance + 非 GT persona（region/role）。"""
    hist_block = "\n".join(f"- {h}" for h in history[-5:]) if history else "(无)"
    claim_block = json.dumps(claim_context or {}, ensure_ascii=False)
    user = f"""persona_context: {json.dumps(persona_context, ensure_ascii=False)}
claim_context: {claim_block}
history: 
{hist_block}

utterance: {utterance}

请完成 ReCon 两阶段分析（JSON）。"""
    return system, user


def build_normalize_prompt(
    *,
    utterance: str,
    turn_index: int,
    default_region: str,
    week: str,
    recon: dict[str, Any],
    conversation_context: list[dict[str, str]],
) -> tuple[str, str]:
    """Normalize 层：RAW + ReCon + 上下文 → canonical slots（ADR-009）。"""
    ctx = _format_history(conversation_context, limit=8)
    system = """你是 Normalize 层（铁矿石市场 claim 转译器）。

任务：结合 **本句 raw utterance**、**ReCon 欺骗分析**、**近期对话上下文**，
将客户多样化表述转译为标准 ontology 槽位。不是逐词翻译，而是语义级标准化。

## regions（严格）
青岛港 | 日照港 | 唐山

## indicators（严格）
港存 | 到港量 | 疏港量 | 采购积极性 | 报价松动 | 利润 | 压港 | 发运

## values（严格枚举，禁止自造词）
- 港存/到港量/疏港量/利润/压港/发运 → 高 | 中 | 低
- 采购积极性 → 积极 | 消极 | 中性
- 报价松动 → 是 | 否（「没松动/尚未松动」→ 否）
- 趋势类表述 → 上涨 | 下跌 | 平稳（仅当用户明确谈价格/走势时）

## 口语→canonical 示例（采购积极性必须用采购枚举，禁止用高/中/低）
偏高/很多/货多/库存多 → 港存=高；中等/还算稳定 → 港存=中；偏少/紧张 → 港存=低
采购不错/旺盛 → 采购积极性=积极；疲软/差 → 采购积极性=消极
还行/一般/随行就市/按需/正常/中性 → 采购积极性=中性（禁止写成「中」）
没松动/尚未松动/报价稳 → 报价松动=否；让利/暗降/松动 → 报价松动=是

## region 归属（防漂移）
- 默认用 default_region；仅当用户**明确断言**另一港口时才换 region
- agent 上一句提到日照港/唐山 ≠ 用户在谈该港；用户说「那边不清楚」→ 不要为该港建槽

## ReCon 调制规则
- deception_score 高：降低 confidence，rationale 注明「策略性/模糊表述」
- rebuttal_language / 纠正语气：可提高 confidence（客户在纠正先前误解）
- 打太极/拒答/「说不准」：返回空槽，宁缺勿滥

## 输出 JSON（仅 JSON）
{
  "normalized_slots": [
    {
      "region": "青岛港",
      "indicator": "港存",
      "value": "中",
      "confidence": 0.85,
      "evidence_span": "原文片段",
      "normalize_rationale": "为何如此转译（含上下文/ReCon）"
    }
  ]
}
无有效指标时返回 {"normalized_slots": []}"""
    user = f"""week: {week}
default_region: {default_region}
turn_index: {turn_index}
utterance: {utterance}

recon:
deception_score: {recon.get('deception_score', 0)}
signals: {json.dumps(recon.get('signals', []), ensure_ascii=False)}
first_order: {recon.get('first_order', '')}
second_order: {recon.get('second_order', '')}

近期对话上下文:
{ctx}

请 normalize 转译（JSON）。"""
    return system, user


def build_fusion_prompt(
    *,
    turns: list[dict[str, Any]],
    per_turn_claims: list[dict[str, Any]],
    default_region: str,
    week: str,
) -> tuple[str, str]:
    """Session-level semantic fusion: dialogue + per-turn claims → final slots."""
    system = """你是 Session Fusion 层（用户最终立场综合器）。

任务：阅读**整段对话**与**逐轮 Normalize claim**，输出该用户对本 session 每个
(region, indicator) 的**最终立场**。不是 last-wins，也不是简单投票。

## 融合原则
1. 语义等价合并：还行 / 一般 / 按需 / 随行就市 / 中性 → 采购积极性=中性
2. 澄清优先：追问后的明确表态 > 早期模糊表述；纠正/反驳覆盖先前错误槽
3. 打太极/拒答/「说不准」→ 该指标不输出（宁缺勿滥）
4. region 防漂移：默认 default_region；仅用户明确断言其他港口才换
5. 每个槽必须给出 evidence_turns（支撑该最终值的 turn_index 列表）

## values（严格枚举）
- 港存/到港量/疏港量/利润/压港/发运 → 高 | 中 | 低
- 采购积极性 → 积极 | 消极 | 中性（禁止用「中」）
- 报价松动 → 是 | 否

## 输出 JSON（仅 JSON）
{
  "final_slots": [
    {
      "region": "青岛港",
      "indicator": "港存",
      "value": "中",
      "confidence": 0.85,
      "evidence_turns": [3, 7],
      "rationale": "为何取该最终值"
    }
  ]
}
无有效最终立场时返回 {"final_slots": []}"""

    dialogue = "\n".join(
        f"[{t.get('turn_index', i)}] {t.get('speaker', '?')}: {t.get('text', '')}"
        for i, t in enumerate(turns)
    )
    claims_txt = "\n".join(
        f"- turn={c.get('turn_index')} {c.get('region')}/{c.get('indicator')}="
        f"{c.get('value')} (conf={c.get('confidence', 0):.2f})"
        for c in per_turn_claims
    ) or "(无逐轮 claim)"
    user = f"""week: {week}
default_region: {default_region}

对话全文:
{dialogue}

逐轮 Normalize claims:
{claims_txt}

请输出该用户最终槽位（JSON）。"""
    return system, user
