"""live 러너가 **이 레포**를 테스트하는지 — 결정적 계약(LLM 호출 없음).

실사고(2026-09-05): 러너 docstring 은 "레포 루트에서 실행하면 레포 스킬이 탐색된다"
고 적었지만 Claude Code 는 cwd 의 임의 `skills/` 를 보지 않는다. 이 머신의 개인
스킬이 2026-06 설치된 **v1.5.0** 이었고, live 스위트는 몇 달째 레포가 아니라 그
사본을 재고 있었다. `fx_guard_overedit` 3건이 브랜치와 무관하게 늘 실패한 이유다 —
레포 스킬(v2.4.0)을 실제로 로드하자 같은 픽스처가 통과했다.

이 테스트는 그 회귀를 코드로 막는다.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import unittest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
_RUNNER = os.path.join(_ROOT, "tests", "humanize_runner.py")


def _load():
    spec = importlib.util.spec_from_file_location("_runner", _RUNNER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class RunnerContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.m = _load()
        with open(_RUNNER, encoding="utf-8") as f:
            self.src = f.read()

    def test_loads_repo_as_plugin(self) -> None:
        """전역 설치본이 아니라 레포를 로드해야 한다."""
        self.assertIn('"--plugin-dir"', self.src)

    def test_repo_skill_version_matches_manifest(self) -> None:
        """러너가 대사하는 기준값이 배포 매니페스트와 같은 값인지."""
        with open(os.path.join(_ROOT, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
            manifest = json.load(f)["version"]
        self.assertEqual(self.m.repo_skill_version(), manifest)

    def test_prompt_requests_version_tag(self) -> None:
        """어느 사본이 응답했는지 출력으로 확인할 수 있어야 한다."""
        prompt = self.m._prompt("텍스트", False)
        self.assertIn("<<<V>>>", prompt)
        self.assertIn("version", prompt)

    def test_version_mismatch_is_not_silently_accepted(self) -> None:
        """버전이 어긋나면 통과가 아니라 '테스트 못 했다'로 끝나야 한다."""
        self.assertIn("SkillUnavailable", self.src)
        self.assertRegex(self.src, r"!=\s*레포 v|다른 사본이 응답했다")
        self.assertIsNotNone(self.m._VERSION_TAG.search("<<<V>>>2.4.0<<</V>>>"))
        self.assertIsNone(self.m._VERSION_TAG.search("버전 없음"))


if __name__ == "__main__":
    unittest.main()
