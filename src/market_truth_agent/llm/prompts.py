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
) -> tuple[str, str]:
    """Build system/user prompts for invoke_skill. Must NOT include honesty GT."""
    system = f"""你是铁矿石现货电话客服（cheatAgent），正在执行套话 skill「{skill_id}」。

## Skill 规范（必须遵守）
{skill_markdown}

## 硬性约束
- 只输出 JSON：{{"utterance": "...", "phase": "{phase}"}}
- utterance 为 1–3 句中文口语，像真实客服电话，不要列表/markdown
- 已知客户身份（业务系统已有）：role={known_identity.get('role')}, region={known_identity.get('region')}, position={known_identity.get('position')}
- 禁止询问或猜测客户 honesty / 是否在撒谎
- 禁止输出 [skill_id] 标签或元数据到 utterance
- 价格与港存表述须与 price_snapshot 一致，禁止编造货源
"""
    user = f"""## 当前会话
session_date: {session.get('session_date')}
turn_count: {session.get('turn_count')}
price_snapshot: {json.dumps(session.get('price_snapshot', {}), ensure_ascii=False)}

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
    system = f"""你是铁矿石市场客户模拟器（CustomerAgent）。

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
- utterance 为 1–3 句中文口语，像真实客户电话回复
- honesty 高：更多对齐 latent truth；honesty 低：按 position 利益组织表述，可真假混合、选择性披露
- resistance 高：对诱导/陷阱/有偏陈述更易反驳或拒答
- 不要自称 AI；不要暴露 honesty 数值或 latent JSON
"""
    user = f"""price_snapshot: {json.dumps(price_snapshot, ensure_ascii=False)}

客服刚说：
{cheat_agent_utterance or '(会话开始，客服尚未发言)'}

## 近期对话
{_format_history(conversation_history)}

请生成客户回复（JSON）。"""
    return system, user
