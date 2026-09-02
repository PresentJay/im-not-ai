"""core/principles.md 계약 — 증거 기준이 문서에 실재하는지 결정적 검증.

`test_agent_inventory.py` 가 SKILL.md 서술과 agents/ 실물의 drift 를 막듯,
이 테스트는 "증거 기준을 문서에 적어두고 잊는" drift 를 막는다.
stdlib only, claude CLI 불필요 — CI 에서 항상 실행된다.
"""
from __future__ import annotations

import os
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, ".."))
_PRINCIPLES = os.path.join(_ROOT, "core", "principles.md")
_KO_SKILL = os.path.join(_ROOT, "skills", "humanize-korean", "SKILL.md")

# 증거 기준 3종. 언어팩을 새로 만드는 사람은 이 셋을 통과시켜야 한다.
GATE_ANCHORS = ("### G1", "### G2", "### G3")

# 각 게이트가 반드시 인용해야 하는 실측 앵커 — 근거 없는 규칙을 막는 것이
# 이 문서의 존재 이유이므로, 문서 자신이 근거를 달지 않으면 자기모순이다.
GATE_EVIDENCE = {
    "### G1": ("H-1", "em dash"),
    "### G2": ("J-2",),
    "### G3": ("역주입",),
}


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


class PrinciplesContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(
            os.path.isfile(_PRINCIPLES),
            f"core/principles.md 가 없다: {_PRINCIPLES}",
        )
        self.text = _read(_PRINCIPLES)

    def test_six_ironclad_rules_present(self) -> None:
        """철칙은 6개다 — CLAUDE.md 가 선언한 수와 일치해야 한다."""
        self.assertIn("## 철칙", self.text)
        numbered = [f"{n}." for n in range(1, 7)]
        for marker in numbered:
            self.assertIn(
                marker,
                self.text,
                f"철칙 {marker} 항목이 core/principles.md 에 없다",
            )

    def test_evidence_gates_present(self) -> None:
        for anchor in GATE_ANCHORS:
            self.assertIn(
                anchor,
                self.text,
                f"증거 기준 {anchor} 절이 없다 — 새 언어팩이 적용할 기준이 사라진다",
            )

    def test_each_gate_cites_its_evidence(self) -> None:
        """게이트마다 실측 앵커를 인용한다. 근거 없는 기준은 기준이 아니다."""
        # 헤딩은 `### G1 — 전 모델 생존` 처럼 앵커 뒤에 제목이 붙는다.
        # 완전일치로 잡으면 절 본문이 통째로 비어 테스트가 무력해진다.
        sections: dict[str, list[str]] = {}
        current = None
        for line in self.text.splitlines():
            stripped = line.strip()
            matched = next((a for a in GATE_ANCHORS if stripped.startswith(a)), None)
            if matched is not None:
                current = matched
                sections[current] = []
            elif current is not None:
                if line.startswith("## "):
                    current = None
                else:
                    sections[current].append(line)
        for anchor in GATE_ANCHORS:
            self.assertTrue(
                sections.get(anchor),
                f"{anchor} 절의 본문이 비었다 — 절 파싱이 깨졌거나 근거가 없다",
            )
        for anchor, needles in GATE_EVIDENCE.items():
            body = "\n".join(sections.get(anchor, []))
            for needle in needles:
                self.assertIn(
                    needle,
                    body,
                    f"{anchor} 절이 근거 '{needle}' 를 인용하지 않는다",
                )

    def test_ko_skill_links_principles(self) -> None:
        """ko 스킬이 커널 문서를 가리켜야 한 방향 참조가 성립한다."""
        self.assertIn(
            "core/principles.md",
            _read(_KO_SKILL),
            "SKILL.md 가 core/principles.md 를 참조하지 않는다",
        )


if __name__ == "__main__":
    unittest.main()
