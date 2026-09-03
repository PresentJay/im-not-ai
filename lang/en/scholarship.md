# Humanize English — Scholarship Reference (v0.1)

> 영어 룰북(`quick-rules.md`)의 학술 인용 SSOT. 한국어 `scholarship.md` 의 대응물.
> 등급 정의는 `core/principles.md` 「근거 등급 (E1~E4)」.
>
> **한국어와의 비대칭**: 한국어는 학술이 없어 코퍼스를 직접 지어야 했다
> (`empirical-validation.md`: "통계적 유의성을 보고한 한국어 번역투 연구가 사실상 없다").
> 영어는 반대다 — 동료심사 발표가 풍부하고, 규칙을 발표 수치로 세울 수 있다.
> **이건 이식 손실이 아니라 이식 이득이다.**

---

## ⚠️ 정정 기록 — 이 문서가 실제로 잡아낸 것

**2026-09-03.** 룰북 v0.1 의 Tier A 7규칙 중 **3개가 방향이 반대**였음이 학술 확인
과정에서 드러났다. 원인은 두 가지가 겹쳤다.

1. **한국어에서 이식**했다 — 한국어 A-9(피동)·G-1/G-2(완곡)는 한국어 실측 근거가
   있지만, 그 방향이 영어에서도 같다는 보장이 없었다.
2. **PDF 페치 요약을 믿었다** — Reinhart et al. 2025 을 요약 도구로 읽었고, 그 요약이
   "passives: LLM 과다"라고 했다. **본문 확인 결과 정반대다.**

이것이 `core/principles.md` 의 E2 등급에 "**본문 표를 직접 확인했는지 별도 표기**"
단서를 단 이유이고, 그 단서가 실제로 발동한 첫 사례다.

| 규칙 | v0.1 처방 | 학술 실측 | 조치 |
|---|---|---|---|
| **A-9** 수동태 | "행위자를 주어로 올려라" | LLM 의 **agentless passive 는 인간의 절반** | **철회** — 손대지 않는다 |
| **G-1** 관측형 완곡 | "단언으로 바꿔라" | LLM 이 hedge 를 **유의하게 적게** 쓴다 | **반전** — 보호 대상 |
| **G-2** 이중 완곡 | "완곡 하나만 남겨라" | 위와 동일 | **반전** — 보호 대상 |

---

## Tier A — 규칙별 학술 앵커

### E-1. 문장 길이 분산 부족 — **유지, 처방 수정**

- **LLM 은 인간보다 문장이 길고, 변이는 작다.** Reinhart et al. 은 LLM 이 "longer and
  more complex sentences" 를 쓰고 information density 가 높다고 보고한다.
- 자체 스파이크 실측(E3): AI 에세이 문장길이 표준편차 6.7~6.8 vs 대조 16.3~18.8.
  교차모델(E3): haiku 6.41 · opus 8.39 · sonnet 9.91 — 체급이 낮을수록 균일.
- ⚠️ **처방 정정**: v0.1 은 한국어 E-1("장문 부재")을 그대로 옮겨 "35어 이상 장문을
  더하라"고 했다. **영어에서는 반대다** — LLM 문장은 이미 길다. 분산을 올리려면
  **짧은 문장을 넣어야 한다.**
- _source_anchor: Reinhart, Markey, Laudenbach, Pantusen, Yurko, Weinberg, Brown (2025),
  "Do LLMs write like humans? Variation in grammatical and rhetorical styles", PNAS 122,
  e2422455122 · arXiv:2410.16107 · **E2, 본문 표 미확인(저자 노트북·소속기관 보도 교차확인)**_

### F-4. 명사화 과다 — **유지, 근거 강함**

- **LLM 은 명사화를 인간의 1.5~2배**로 쓴다(Reinhart). 독립 재현: Mizumoto et al. 은
  ChatGPT 에세이가 "more nominalization" 을 보인다고 보고하고, Jiang & Hyland 는
  "noun/preposition-based bundles" 가 ChatGPT 에 더 흔하다고 한다.
- **3개 연구 독립 수렴** — 영어 룰북에서 근거가 가장 단단한 항목이다.
- 이론 토대: Biber 의 MDA 차원 1(informational vs involved production). 명사화·전치사구는
  informational 극의 핵심 지표다. LLM 이 "informationally dense, noun-heavy style" 로
  훈련됐다는 Reinhart 의 해석과 맞물린다.
- _source_anchor: Reinhart et al. 2025 PNAS; Mizumoto, Yasuda, Tamura (2024),
  "Identifying ChatGPT-generated texts in EFL students' writing", Applied Corpus Linguistics;
  Jiang & Hyland (2025), English for Specific Purposes 79: 17-29 · **E2 ×3**_

### EN-1. 현재분사절 과다 — **신규, 최대 효과**

- **LLM 은 present participial clause 를 인간의 2~5배**로 쓴다. Reinhart et al. 이
  보고한 **가장 큰 차이 중 하나**다.
- 예: "…, gathering clauses as it goes", "…, highlighting the need for…",
  "…, reflecting a broader shift".
- 처방: 종속절·독립문으로 푼다. `X, reflecting Y` → `X. That reflects Y.` /
  `X, which reflects Y`. **내용을 추가하지 않는다.**
- ⚠️ v0.1 룰북에 **없었다.** 최대 효과 항목을 빠뜨렸다. 한국어 대응물이 없어
  영어 고유 ID(`EN-*`)를 새로 부여한다.
- _source_anchor: Reinhart et al. 2025 PNAS · **E2**_

### F-7. 범용 동사·초과 어휘 — **유지, 원자료 확인**

- Kobak et al. 은 PubMed 초록 15M편(2010–2024)에서 excess vocabulary 를 채굴했고,
  **2024 초과 어휘의 66% 가 동사**다(delve·underscore·showcase). 공개 원자료
  `results/excess_words.csv` 를 직접 재계산해 **65.8%** 로 검증했다.
- Reinhart 계열은 어휘 편향을 다른 각도로 재현한다 — ChatGPT 가 `camaraderie`·`tapestry`
  를 인간의 **약 150배**, Llama 가 `unease` 를 **60~100배**, 양쪽이 `palpable`·`intricate`
  선호.
- ⚠️ **자체 실측 반증(E3)**: 현세대 Claude 출력 20편에서 라우터 렉시콘 **0건**,
  전수 407건으로도 12.6~33.5/1k 이며 **모델 체급을 탄다**(haiku 33.5 > opus 18.5 >
  sonnet 12.6). Kobak 코퍼스는 2024년까지이고 생의학 초록이다. **이 층은 최신 대형
  모델에서 상당 부분 사라졌다** — 규칙은 유지하되 발화 기대치를 낮게 잡는다.
- _source_anchor: Kobak, Márquez, Horvát, Lause (2025), "Delving into LLM-assisted writing
  in biomedical publications through excess vocabulary", Science Advances ·
  arXiv:2406.07016 · 데이터 github.com/berenslab/llm-excess-vocab ·
  **E2, 원자료 직접 확인**_

### C-8. Antithesis 대구 — **등급 하향**

- 한국어에서는 최강 신호다 — 12.1배, 전 모델, 과업 무관(E1).
- **영어 학술 근거는 없다.** 블로그·해설이 "not just X, but Y" 를 LLM hallmark 로
  지목하지만 계량 연구를 찾지 못했다. 구문복잡도 연구가 ChatGPT 의 coordination
  구조 선호·병렬 구문 의존을 보고하는 것이 가장 가까운 간접 근거다.
- ⚠️ **아이러니**: 이 프로젝트가 "영어 최강 신호"로 밀어온 항목이 영어 근거가 가장 약하다.
  한국어 E1 의 이식이지 영어 실측이 아니다.
- _source_anchor: 한국어 `empirical-validation.md` C-8 이식 · **E3(영어 미검증)**_

---

## 결핍 신호 — LLM 이 **적게** 쓰는 것

여기가 v0.1 이 통째로 놓친 축이다. 그리고 **일부는 제거하면 안 되는 것을 제거하고 있었다.**

### 완곡·서법 (hedges · boosters · modals) — **보호 대상**

**3개 연구가 독립적으로 수렴한다.**

| 출처 | 발견 |
|---|---|
| Jiang & Hyland 2025 (ESP 79:17-29) | ChatGPT 에세이가 hedges·boosters·attitude markers 등 **interactional metadiscourse 를 유의하게 적게** 쓴다. 결과적으로 impersonal·expository 한 톤 |
| Mizumoto et al. 2024 (Applied Corpus Linguistics) | **인간** 에세이가 modals·epistemic markers·discourse markers 를 **더 많이** 쓴다 |
| Reinhart et al. 2025 (PNAS) | 같은 방향(hedges/downtoners) |

→ **`may`·`might`·`appears to`·`tends to`·`arguably` 를 제거하면 글이 더 AI처럼 된다.**
그리고 학술·논증 텍스트에서는 **주장의 강도를 바꾸는 내용 변경**이기도 하다(철칙 #1).

이론 토대: Hyland 의 metadiscourse 프레임(interactive vs interactional). hedging 은
학술 영어의 **규범**이지 군더더기가 아니다.

_source_anchor: Jiang & Hyland 2025 ESP 79: 17-29; Mizumoto et al. 2024;
Reinhart et al. 2025 PNAS · **E2 ×3**_

### Agentless passive — **손대지 않는다**

- **LLM 은 agentless passive 를 인간의 절반**만 쓴다(Reinhart et al.).
- 따라서 "행위자를 주어로 올려라"는 처방은 글을 AI 쪽으로 민다.
- 다만 "수동태를 늘려라"도 하지 않는다 — 결핍 신호 정책상 **처방 불가, 관측 전용**이다
  (`core/principles.md` 「결핍 신호 정책」).

_source_anchor: Reinhart et al. 2025 PNAS · **E2**_

### 1·2인칭 대명사 · contraction · discourse marker

- LLM 이 personal reference 를 적게 쓴다(Goulart et al., Reinhart 경유).
- contraction 과소 사용 — 원문의 contraction 을 펴면 티가 늘어난다(철칙 #5).
- **관측 전용.** 없는 인칭을 심으면 문체가 아니라 화자가 바뀐다.

---

## Caveat

**C1. 코퍼스 장르 불일치.** Kobak 은 생의학 초록, Jiang & Hyland 와 Mizumoto 는 학생
논증 에세이, Reinhart 는 여러 장르 혼합. 이 스킬의 주 사용처(칼럼·블로그·리포트)와
정확히 겹치지 않는다. **방향 근거이지 임계가 아니다.**

**C2. 본문 표 미확인.** Reinhart·Kobak·Jiang & Hyland 모두 초록·저자 노트북·소속기관
보도·검색 요약으로 확인했다. Kobak 만 공개 원자료를 직접 재계산했다. 나머지는
수치를 인용할 때 이 한계를 함께 적는다. **v0.1 의 A-9 오류가 정확히 이 지점에서 났다.**

**C3. 모델 세대 이동.** Kobak 은 2024년까지, Reinhart 는 GPT-4o·Llama 3, Jiang & Hyland
와 Mizumoto 는 ChatGPT(3.5/4 세대). 자체 실측(2026-09, Claude 계열)에서 어휘 층은
이미 크게 약해졌다. **어휘 규칙은 유효기간이 짧다고 가정한다.**

**C4. E1 부재.** 영어에는 자체 대조 코퍼스가 없다. 인간 영어 기준선을 재본 적이 없어
"분산 8.59 가 인간 범위인가"에 답할 수 없다. `core/principles.md` E3 조항에 따라
**영어 임계는 전부 잠정이며 heavy·finalize 경로를 열지 않는 근거**가 된다.

**C5. Biber·Hyland 원전 미확인.** MDA 차원과 metadiscourse 프레임은 2차 인용으로만
확인했다. 이론 토대로만 쓰고, 수치를 여기서 끌어오지 않는다.

---

## 참고 문헌

- Reinhart, A., Markey, B., Laudenbach, M., Pantusen, K., Yurko, R., Weinberg, G.,
  Brown, D. W. (2025). *Do LLMs write like humans? Variation in grammatical and
  rhetorical styles*. PNAS 122, e2422455122. arXiv:2410.16107.
  저자 노트북: refsmmat.com/notebooks/llm-style.html
- Kobak, D., Márquez, R. G., Horvát, E.-Á., Lause, J. (2025). *Delving into LLM-assisted
  writing in biomedical publications through excess vocabulary*. Science Advances.
  arXiv:2406.07016. 데이터: github.com/berenslab/llm-excess-vocab
- Jiang, F. (K.), Hyland, K. (2025). *Rhetorical distinctions: Comparing metadiscourse in
  essays by ChatGPT and students*. English for Specific Purposes 79: 17-29.
- Mizumoto, A., Yasuda, S., Tamura, Y. (2024). *Identifying ChatGPT-generated texts in
  EFL students' writing: Through comparative analysis of linguistic fingerprints*.
  Applied Corpus Linguistics.
- Rudnicka, K., Juzek, T. S. (2026). *Beyond "AI Language": The case for the idiolectal
  nature of LLM output*. arXiv:2608.06589. **E3 — 프리프린트.**
- SlopDetector (2026). *Is the Em Dash an AI Tell?* 인간 702,939 words vs 6모델.
  **E3 — 비심사, 인간 풀이 문학 고전.**
- Biber, D. (1988). *Variation across Speech and Writing*. **E4 — 2차 인용, 이론 토대.**
- Hyland, K. (2005). *Metadiscourse: Exploring Interaction in Writing*.
  **E4 — 2차 인용, 이론 토대.**
