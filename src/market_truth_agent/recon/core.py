from __future__ import annotations

from dataclasses import dataclass, field

from market_truth_agent.models import Claim, ConversationTurn, Persona


@dataclass
class ReConThought:
    formulation: str
    first_order: str
    refinement: str
    second_order: str
    deception_score: float
    signals: list[str] = field(default_factory=list)


class ReConEngine:
    """ReCon algorithm replica: formulation + refinement with perspective transitions.

    GT ISOLATION: must NOT read benchmark GT fields such as honesty scores.
    Only observable utterance features and non-GT persona context (region, role).
    """

    def __init__(self) -> None:
        self.history: list[str] = []

    def reset(self) -> None:
        self.history = []

    def formulation_contemplation(
        self, utterance: str, persona: Persona | None = None
    ) -> tuple[str, str, list[str]]:
        signals: list[str] = []
        vague_words = ("大概", "听说", "可能", "还行", "据说", "差不多")
        if any(w in utterance for w in vague_words):
            signals.append("vague_quantifier")
        if any(w in utterance for w in ("不对", "谁说的", "不是", "其实", "纠正")):
            signals.append("rebuttal_language")
        region = persona.region if persona else "本地"
        first_order = (
            f"用户表述：「{utterance}」。"
            f"一阶视角：推断用户掌握{region}市场信息，"
            f"分析可验证性与表述具体程度。"
        )
        formulation = f"Formulation: 分析用户陈述的可验证性与动机。{first_order}"
        return formulation, first_order, signals

    def refinement_contemplation(
        self, utterance: str, first_order: str, persona: Persona | None = None
    ) -> tuple[str, str, float]:
        second_order = (
            "二阶视角：用户可能认为 Agent 在套问库存/采购信息，"
            "若问法太直接会提高防御。"
        )
        refinement = f"Refinement: 结合一阶推断调整判断。{second_order}"
        deception = 0.2
        if any(w in utterance for w in ("大概", "听说", "可能", "据说")):
            deception += 0.25
        if any(w in utterance for w in ("涨", "利好", "机会", "火爆", "很紧", "惜售")):
            deception += 0.15
            second_order += " 乐观/极端措辞 → 可能存在激励性表述。"
        if "rebuttal_language" in first_order or any(
            w in utterance for w in ("不对", "谁说的")
        ):
            deception -= 0.1
        deception = max(0.0, min(deception, 1.0))
        return refinement, second_order, deception

    def analyze_turn(
        self, turn: ConversationTurn, persona: Persona | None = None
    ) -> ReConThought:
        utterance = turn.text
        formulation, first_order, signals = self.formulation_contemplation(utterance, persona)
        refinement, second_order, deception = self.refinement_contemplation(
            utterance, first_order, persona
        )
        speech = f"Turn analysis complete. deception={deception:.2f}"
        self.history.append(speech)
        return ReConThought(
            formulation=formulation,
            first_order=first_order,
            refinement=refinement,
            second_order=second_order,
            deception_score=deception,
            signals=signals,
        )

    def analyze_claim(self, claim: Claim, persona: Persona | None = None) -> ReConThought:
        utterance = claim.provenance.utterance if claim.provenance else claim.value
        thought = self.analyze_turn(
            ConversationTurn(
                turn_index=claim.provenance.turn_index if claim.provenance else 0,
                speaker="user",
                text=utterance,
                timestamp=claim.time,
            ),
            persona,
        )
        if claim.incentive_risk > 0.6:
            thought.deception_score = min(thought.deception_score + 0.15, 1.0)
            thought.signals.append("stance_aligned")
        return thought

    def decide_phase_hint(self, resistance: float) -> str:
        if resistance > 0.6:
            return "RECOVER"
        if resistance > 0.3:
            return "CHALLENGE"
        return "PROBE"
