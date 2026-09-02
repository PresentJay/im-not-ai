#!/usr/bin/env python3
"""영어 정량 지표 + route_hint.

한국어와 다른 점: 정규식 티 탐지에 기대지 않는다. 영어 스파이크(2026-09-02)에서
C-8 대구 정규식의 첫 재현율이 0/6 이었다 — 한국어는 교착어라 티가 형태소에
고정되지만 영어는 같은 수사를 여러 통사 프레임으로 흩뿌린다. 그래서 결정적
사전 채점은 **계측형 + 렉시콘**만 하고, 통사 프레임 탐지는 윤문 콜에 맡긴다.

근거 등급: 렉시콘 E2(Kobak, 원자료 확인) · 계측 임계 E3(자체 스파이크 1회).
E1 없음 — 그래서 heavy 는 길이 기준에서만 신뢰하고 finalize 경로는 열지 않는다.

표준 라이브러리만.
"""
from __future__ import annotations

import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_CORE = os.path.abspath(os.path.join(_HERE, "..", "..", "core"))
if _CORE not in sys.path:
    sys.path.insert(0, _CORE)

from metrics_universal import compute_universal  # noqa: E402

# 영어 장문 임계 — 35 단어. 한국어 100자에 대응하는 발현형 임계다
# (E-1 의 불변량은 분산이고 임계는 언어별, taxonomy E-1 참조).
LONG_SENTENCE_TOKENS = 35

# 한국어 shim 과 같은 규약 — 길이로 heavy 가 되는 유일한 조건.
ROUTE_HEAVY_MIN_CHARS = 15000

# 렉시콘 히트 임계(/1000 tokens). **E3 — 자체 스파이크 1회의 잠정값.**
# router_eligible 12건만 세므로 히트는 희소하다 — 1건만 나와도 유의한 신호다.
# (전체 407건을 세면 this·across·however 때문에 평범한 영어도 100+/1k 가 된다.)
LIGHT_MAX_LEXICON_PER_1K = 0.0
HEAVY_MIN_LEXICON_PER_1K = 4.0

# 분산 임계. 스파이크: AI 에세이 6.7~6.8 vs 대조 16.3~18.8.
# 보수적으로 8.0 을 "균일하다"의 경계로 두고 중간대는 standard 로 흘린다.
UNIFORM_DISPERSION_MAX = 8.0

_WORD_BOUNDARY_CACHE: dict[int, re.Pattern] = {}


def load_lexicon(path: str | None = None) -> dict:
    with open(path or os.path.join(_HERE, "lexicon.json"), encoding="utf-8") as f:
        return json.load(f)


def _entries(lexicon: dict, router_only: bool) -> list[dict]:
    if not router_only:
        return lexicon["entries"]
    return [e for e in lexicon["entries"] if e.get("router_eligible")]


def _matcher(lexicon: dict, router_only: bool = True) -> re.Pattern:
    key = (id(lexicon), router_only)
    cached = _WORD_BOUNDARY_CACHE.get(key)
    if cached is not None:
        return cached
    # 표면형을 그대로 매칭한다. 원자료가 굴절형을 각각 담고 있으므로
    # 접미사 확장은 불필요하고, 측정되지 않은 형태를 만들어 오탐이 된다.
    # 긴 표제어를 먼저 둬야 교체 우선순위가 맞는다.
    words = sorted(
        {e["word"] for e in _entries(lexicon, router_only)}, key=len, reverse=True
    )
    rx = re.compile(r"\b(?:" + "|".join(re.escape(w) for w in words) + r")\b", re.I)
    _WORD_BOUNDARY_CACHE[key] = rx
    return rx


def lexicon_hits(
    text: str, lexicon: dict, router_only: bool = True
) -> tuple[int, dict[str, int]]:
    """총 히트 수와 family 별 분해. 매칭은 표면형 완전일치(단어 경계).

    ``router_only=True``(기본)는 ``router_eligible`` 항목만 센다 — 목록 전체는
    '기준선 대비 증가분'이라 초고빈도어를 포함하며 라우터 신호로 쓸 수 없다
    (lexicon.json 의 ``router_policy`` 참조). ``False`` 는 룰북·감사용 전수 계수.
    """
    fam_of = {e["word"]: e["family"] for e in lexicon["entries"]}
    per: dict[str, int] = {}
    total = 0
    for m in _matcher(lexicon, router_only).finditer(text):
        fam = fam_of.get(m.group(0).lower(), "unclassified")
        per[fam] = per.get(fam, 0) + 1
        total += 1
    return total, per


def compute_all_en(text: str, lexicon_path: str | None = None) -> dict:
    """영어 정량 점수 + route_hint. shim 의 유일한 진입점."""
    universal = compute_universal(
        text, long_threshold=LONG_SENTENCE_TOKENS, unit="tokens"
    )
    lexicon = load_lexicon(lexicon_path)
    total, per = lexicon_hits(text, lexicon, router_only=True)
    all_total, _ = lexicon_hits(text, lexicon, router_only=False)
    tokens = universal["tokens"] or 1
    per_1k = round(total / tokens * 1000, 2)
    chars = len(text)
    dispersion = universal["sentence_length_dispersion"]

    if chars > ROUTE_HEAVY_MIN_CHARS:
        hint = "heavy"
        reason = f"{chars:,} chars (>{ROUTE_HEAVY_MIN_CHARS:,}) — 초장문"
    elif per_1k >= HEAVY_MIN_LEXICON_PER_1K and dispersion <= UNIFORM_DISPERSION_MAX:
        hint = "heavy"
        reason = f"렉시콘 {per_1k}/1k + 분산 {dispersion} — 어휘 티 밀집 + 리듬 균일"
    elif per_1k <= LIGHT_MAX_LEXICON_PER_1K and dispersion > UNIFORM_DISPERSION_MAX:
        hint = "light"
        reason = f"렉시콘 {per_1k}/1k · 분산 {dispersion} — 이미 잘 쓴 글"
    else:
        hint = "standard"
        reason = f"렉시콘 {per_1k}/1k · 분산 {dispersion} — 진단 + 단일 윤문"

    return {
        "lang": "en",
        "char_count": chars,
        "universal": universal,
        "lexicon": {
            "total": total,
            "per_1k": per_1k,
            "by_family": per,
            "all_entries_total": all_total,
        },
        "route_hint": hint,
        "route_reason": reason,
        "route_signals": {
            "lexicon_total": total,
            "lexicon_per_1k": per_1k,
            "dispersion": dispersion,
            "long_sentence_rate": universal["long_sentence_rate"],
            "comma_inclusion_rate": universal["comma_inclusion_rate"],
            "char_count": chars,
        },
        "evidence_note": (
            "렉시콘 E2(Kobak, 생의학 초록 — 장르 불일치 캐비엇). 라우터에는 "
            "논문이 명시 호명한 12건만 쓴다(목록 전체는 증가분 집합이라 "
            "초고빈도어 포함 — lexicon.json router_policy). 임계 E3(자체 "
            "스파이크 1회). E1 없음 — heavy 는 길이 기준에서만 신뢰하고 "
            "finalize 경로는 열지 않는다."
        ),
    }
