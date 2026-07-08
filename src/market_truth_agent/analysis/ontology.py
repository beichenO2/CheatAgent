from __future__ import annotations

import re

REGIONS = ["青岛港", "日照港", "唐山"]
INDICATORS = ["港存", "到港量", "疏港量", "采购积极性", "报价松动", "利润", "压港", "发运"]
ORDINAL_MAP = {
    "高": "高", "偏高": "高", "很多": "高", "充足": "高", "不紧": "高", "库存多": "高", "货还是多的": "高",
    "中": "中", "还行": "中", "还可以": "中", "一般": "中", "正常": "中", "中等": "中",
    "低": "低", "偏少": "低", "紧张": "低", "不多": "低", "紧": "低",
    "积极": "积极", "旺盛": "积极", "不错": "积极", "中性": "中性",
    "消极": "消极", "疲软": "消极", "差": "消极",
    "是": "是", "否": "否", "有": "是", "没有": "否", "松动": "是",
    "涨": "上涨", "上涨": "上涨", "看涨": "上涨",
    "跌": "下跌", "下跌": "下跌", "看跌": "下跌",
    "平": "平稳", "平稳": "平稳", "震荡": "平稳",
}

INDICATOR_ALIASES = {
    "库存": "港存", "港口库存": "港存", "港存": "港存",
    "采购": "采购积极性", "采购积极性": "采购积极性",
    "报价": "报价松动", "价格松动": "报价松动",
    "利润": "利润", "走线": "利润",
}


def detect_region(text: str, default: str = "青岛港") -> str:
    for region in REGIONS:
        if region in text:
            return region
    return default


def detect_indicator(text: str) -> str | None:
    found = detect_all_indicators(text)
    return found[0] if found else None


def detect_all_indicators(text: str) -> list[str]:
    found: list[str] = []
    for alias, indicator in INDICATOR_ALIASES.items():
        if alias in text and indicator not in found:
            found.append(indicator)
    for indicator in INDICATORS:
        if indicator in text and indicator not in found:
            found.append(indicator)
    return found


def normalize_value(text: str, indicator: str) -> str | None:
    if indicator == "报价松动":
        if "没" in text and "松动" in text:
            return "否"
        if "松动" in text or "降价" in text:
            return "是"
    for key in sorted(ORDINAL_MAP, key=len, reverse=True):
        if key in text:
            return ORDINAL_MAP[key]
    return None


def canonicalize(region: str, market_object: str, indicator: str, week: str) -> tuple[str, str]:
    key = f"{week}|{region}|{market_object}|{indicator}"
    return key, key


def infer_claim_type(indicator: str, value: str) -> str:
    if value in ("上涨", "下跌", "平稳"):
        return "directional"
    if indicator == "报价松动":
        return "binary"
    if re.search(r"\d+", value):
        return "numeric"
    return "ordinal"
