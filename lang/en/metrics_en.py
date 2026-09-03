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

# ⚠️ 분산 임계 폐기 (2026-09-03, E1 실측).
# 초판 UNIFORM_DISPERSION_MAX = 8.0 은 **인간 학술 초록 42편 중 21편(50%)을
# AI 로 오판**했다. 스파이크의 '대조군'이 마크다운 표·리스트가 섞인 문서라
# 분산이 16~18 로 부풀려져 있었고, 그걸 인간 범위로 착각한 결과다.
# 실측: 인간 중앙값 8.01 (2.32~16.3) vs AI 6.98 (3.5~12.37) — AUC 0.380,
# |0.5차| 0.120 으로 **판별력 약함**. 라우터 판정에서 뺀다.
#
# 대신 쉼표 계열을 쓴다 — 같은 실측에서 훨씬 강했다:
#   comma_segment_length  AUC 0.149 (|0.5차| 0.351)  AI 가 짧게 끊는다
#   comma_inclusion_rate  AUC 0.719 (|0.5차| 0.219)  AI 가 많이 쓴다
# 임계는 인간 사분위수 기반 (lang/en/baseline.json recommended_thresholds).
COMMA_SEGMENT_AI_MAX = 10.82   # 인간 하위 25% — 이 미만이면 AI 방향
COMMA_INCLUSION_AI_MIN = 73.3  # 인간 상위 25% — 이 초과면 AI 방향

# 밀도 지표를 쓰기 위한 최소 분량. 39토큰 글에서 렉시콘 1건이면 25.6/1k 가
# 나와 heavy 로 튄다 — 비율이 아니라 분모가 만든 수다.
# `core/principles.md` G3 의 "밀도 지표를 볼 때는 분모를 함께 본다"가
# 라우터 자신에게도 적용된다. 이 아래에서는 어휘·분산 판정을 하지 않고
# standard(안전한 기본값)로 보낸다.
MIN_TOKENS_FOR_RATE = 200

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
    elif tokens < MIN_TOKENS_FOR_RATE:
        hint = "standard"
        reason = (
            f"{tokens} tokens (<{MIN_TOKENS_FOR_RATE}) — 밀도 판정 불가, "
            f"기본 경로 (렉시콘 {total}건 · 분산 {dispersion})"
        )
    else:
        seg = universal["comma_segment_length"]
        incl = universal["comma_inclusion_rate"]
        # 판별력 순으로 센다 — 쉼표 절 길이(AUC 0.351) > 쉼표 포함률(0.219).
        signals = []
        if seg and seg < COMMA_SEGMENT_AI_MAX:
            signals.append(f"쉼표 절 {seg}어(<{COMMA_SEGMENT_AI_MAX})")
        if incl > COMMA_INCLUSION_AI_MIN:
            signals.append(f"쉼표 포함률 {incl}%(>{COMMA_INCLUSION_AI_MIN})")
        if per_1k >= HEAVY_MIN_LEXICON_PER_1K:
            signals.append(f"렉시콘 {per_1k}/1k")

        if len(signals) >= 2:
            hint = "heavy"
            reason = "AI 신호 " + " + ".join(signals)
        elif signals:
            hint = "standard"
            reason = "AI 신호 " + " · ".join(signals)
        else:
            hint = "light"
            reason = (
                f"쉼표 절 {seg}어 · 포함률 {incl}% · 렉시콘 {per_1k}/1k — "
                f"인간 범위, 이미 잘 쓴 글"
            )

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
