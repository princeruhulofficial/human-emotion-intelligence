# Research Insights 2026 — Powering HEI

**Date:** July 2026  
**Purpose:** Durable research notes to guide HEI product decisions.

---

## 1. Executive Takeaways

1. **Emotional intelligence in LLMs is fragmented** across perception, cognition, and interaction (FACET / MSCEI four-branch model). Label accuracy ≠ interactive success.
2. **Outcome > taxonomy.** Users pay for *feeling understood*, not for emotion labels.
3. **Multi-layer context wins:** situational + personal + behavioral (IEEE human-context AI).
4. **Memory architecture decides long-term quality.** Multi-tier + emotional salience >> raw context windows.
5. **Theory-backed structure helps:** Plutchik wheel, OCC/appraisal, valence–arousal, time decay.
6. **Ethics is product:** avoid addictive empathy loops, fake intimacy, and overclaiming “feelings.”

---

## 2. Key Papers & Industry Signals

### FACET (2026)
- Psychometrically grounded EI test (perceive → facilitate → understand → manage).
- Frontier models strong on recognition/reasoning; weaker on consistent interactive empathy.
- RLHF often optimizes “stochastic empathy” (syntax mimicry).

**Implication for HEI:** Keep the explicit pipeline (detect → intent → plan → evaluate). Do not collapse into a single “be nice” prompt.

### Human-context AI (IEEE Spectrum)
Three context types:
- Situational / environmental
- Personal (history, goals, baseline)
- Behavioral patterns

**Implication:** Expand beyond turn-level emotion toward relationship and goal context.

### Companion / memory studies
- Few products keep coherent personality/memory past ~30 conversations.
- Emotional weighting of memories beats flat RAG.
- Memory grounding can produce large UX lifts when present.

**Implication:** Persistent backends (SQLite/Redis) + salience + decay are core, not optional polish.

### Open-source emotional engines
| Project | Pattern |
|---------|---------|
| SentiCore | High-dim emotion matrix, time decay, drift |
| Blaniel | OCC + Plutchik + vector memory |
| neurostate | Persistent internal state via MCP |
| Hume AI | Multimodal voice (commercial) |

**HEI differentiation:** Model-agnostic *infrastructure* (SDK + MCP + HTTP), privacy-first, outcome metric “felt understood” — not a character engine.

---

## 3. Theoretical Anchors

### Plutchik’s Wheel
Eight primaries: joy, trust, fear, surprise, sadness, disgust, anger, anticipation.  
Opposites and blends (e.g., joy+trust → love) improve nuance over flat label lists.

### Appraisal / OCC-style signals
Emotions arise from evaluation of events against goals:
- Goal relevance / congruence
- Coping potential
- Agency / blame

Lightweight appraisal fields improve strategy quality without full cognitive simulation.

### MSCEI branches (map to HEI modules)
| Branch | HEI module |
|--------|------------|
| Perceive | Emotion detection |
| Facilitate | Strategy + tone |
| Understand | Intent + memory context |
| Manage | Evaluation + rewrite + safety |

---

## 4. Risks to Explicitly Avoid

- Reward loops of empty praise designed for retention
- Relationship-deepening simulation without transparency
- Presenting inferred emotions as facts
- Crisis handling that pretends to replace professional care

HEI policy: express uncertainty, confidence scores, tentative language, safety scores.

---

## 5. Product Principles (reinforced)

1. **Layer, not model** — works with any LLM.
2. **Outcome-first** — optimize for felt understanding.
3. **Structured, inspectable** — every step is data, not a black-box vibe.
4. **Memory with integrity** — persist what matters; decay what doesn’t.
5. **Honest about limits** — patterns, not feelings.

---

## 6. Sources (selected)

- FACET / emotional intelligence fragmentation in LLMs (arXiv 2026)
- IEEE Spectrum: Emotion AI + human context layers
- Surveys: Affective computing in the LLM era; multimodal emotion recognition
- Plutchik (1982) and applied dialogue/TTS planning papers
- Industry: Hume AI, companion memory benchmarks, MCP-based state engines
- CHI 2026: agentic memory and reciprocal disclosure studies

---

*This document informs `docs/roadmap-v0.4.md` and schema upgrades in v0.4.*
