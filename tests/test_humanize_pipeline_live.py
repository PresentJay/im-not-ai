"""제품 경로 live 테스트 — 스킬을 **파일 생성 허용**으로 정상 실행한다.

`test_humanize_live.py` 는 "파일은 만들지 마"라고 지시해서 shim·게이트가 빠진
경로를 잰다. 그 경로에서 `fx_guard_overedit` 이 변경률 0.55 로 상한을 넘는데,
제품은 그 상황을 `verify_change_rate.py`(50% 이상 기각)로 막는다 — 철칙 #4 가
"판정은 스크립트가 내린다, LLM 자가보고가 아니다"라고 못박은 지점이다.

여기서는 그 보장을 실제로 확인한다: 스킬을 정상 절차로 돌리고, 나온 산출물이
게이트를 통과하는지 결정적으로 잰다.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, ".."))
sys.path.insert(0, _HERE)
import humanize_asserts as ha  # noqa: E402
import humanize_runner as hr  # noqa: E402

with open(os.path.join(_HERE, "fixtures.json"), encoding="utf-8") as _f:
    _FIXTURES = {fx["id"]: fx for fx in json.load(_f)["fixtures"]}

_GUARD = "fx_guard_overedit"


@unittest.skipIf(hr.CLAUDE_BIN is None, "claude CLI 없음 — live 통합 테스트 skip")
class PipelineLiveTests(unittest.TestCase):
    def test_guard_fixture_survives_the_shipped_path(self) -> None:
        fx = _FIXTURES[_GUARD]
        try:
            out, run_dir = hr.run_humanize_pipeline(fx["input_text"])
        except hr.QuotaExhausted as exc:
            self.skipTest(f"사용량 한도 — 측정 불가: {exc}")

        miss = ha.missing_protected_tokens(out, fx.get("protected_tokens", []))
        self.assertEqual(miss, [], f"[{_GUARD}] 보호 토큰 유실: {miss}")

        gate = subprocess.run(
            [sys.executable, os.path.join(_ROOT, "scripts", "verify_change_rate.py"),
             "--before", os.path.join(run_dir, "01_input.txt"),
             "--after", os.path.join(run_dir, "final.md")],
            capture_output=True, text=True, timeout=120,
        )
        self.assertNotEqual(
            gate.returncode, 2,
            f"[{_GUARD}] 게이트가 ABORT 인 산출물이 그대로 남았다 — 제품 보장 실패\n"
            f"{gate.stdout}",
        )
        self.assertNotEqual(gate.returncode, 3, f"게이트 실행 오류: {gate.stderr}")


if __name__ == "__main__":
    unittest.main()
