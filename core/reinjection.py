#!/usr/bin/env python3
"""G3 역주입 게이트 — 윤문 전후를 같은 지표로 재측정한다.

철칙 #6(No New Tells)의 코드화. 지우기로 한 티가 줄었어도 다른 지표가
새로 올랐으면 실패다. **윤문 콜은 티를 지우면서 자기 모델의 개인어를 심는다.**

실측 근거 (`core/principles.md` G3):
- 영어 — 스파이크 윤문에서 목표 지표는 전부 0 으로 내려갔는데 em dash 가
  2→5(9.33/1k)로 늘었다. 장문 부재를 고치려 문장을 이어 붙이면서 접합부에
  대시를 심은 것이다. 발표된 Claude Opus 4.6 = 9.09/1k 와 거의 일치한다.
- 한국어 — D-9 결산 정리가 '결국' 을 역주입해 재실측에서 2→4 로 늘었다.

**원시 건수로 판정한다.** 밀도로 보면 본문이 짧아진 것만으로 상승이 잡혀
오탐이 난다(스파이크 I-4 3.42→3.73, 건수는 2→2 불변).

언어 무관 — 무엇을 셀지는 호출자가 counters 로 주입한다.
"""
from __future__ import annotations

import os
import sys
from typing import Callable

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from metrics_universal import compute_universal  # noqa: E402


def check_reinjection(
    before: str,
    after: str,
    counters: dict[str, Callable[[str], int]],
    *,
    unit: str = "tokens",
    long_threshold: int = 35,
) -> dict:
    """전후를 같은 카운터로 재측정해 신규 상승분을 찾는다.

    반환:
        ``failed``      — 하나라도 올랐으면 True
        ``risen``       — {이름: (before_n, after_n)} 오른 항목만
        ``dispersion``  — (before, after) 문장길이 분산. **판정에 쓰지 않는다**
                          — 분산 상승은 E-1 처방의 의도된 결과이므로 보고만 한다.
        ``note``        — 사람이 읽을 한 줄
    """
    risen: dict[str, tuple[int, int]] = {}
    for name, fn in counters.items():
        b, a = fn(before), fn(after)
        if a > b:
            risen[name] = (b, a)

    bu = compute_universal(before, long_threshold=long_threshold, unit=unit)
    au = compute_universal(after, long_threshold=long_threshold, unit=unit)

    return {
        "failed": bool(risen),
        "risen": risen,
        "dispersion": (
            bu["sentence_length_dispersion"],
            au["sentence_length_dispersion"],
        ),
        "note": (
            "역주입 없음 — 티는 줄기만 했다"
            if not risen
            else "역주입 감지: "
            + ", ".join(f"{k} {b}→{a}" for k, (b, a) in sorted(risen.items()))
        ),
    }
