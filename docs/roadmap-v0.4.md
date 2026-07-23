# HEI Roadmap — v0.4

**Theme:** Theory-backed depth + outcome metrics + smarter memory  
**Base:** v0.3.0 (TS memory parity, persistent backends, CI)

---

## Goals

1. Align emotion taxonomy with **Plutchik-inspired** coverage (keep HEI labels stable where possible).
2. Add lightweight **appraisal** fields to emotion analysis.
3. Make **`felt_understood_score`** a first-class evaluation metric.
4. Add **emotional salience** (and hooks for time decay) to memory turns.
5. Remain **backward compatible** — new fields optional with defaults.

---

## Scope

### In scope

| Item | Description |
|------|-------------|
| Taxonomy expansion | trust, disgust, surprise, anticipation, love, optimism, disappointment, burnout (as needed) |
| Appraisal (optional) | `goal_relevance`, `coping_potential`, `agency` on EmotionResult |
| Evaluation | `felt_understood_score: float` (0–10) |
| Memory | `salience: float` per turn; strategy context prefers high-salience recent turns |
| Docs | research insights + this roadmap |
| Tests | schema/unit coverage for new fields |

### Out of scope (later)

- Full multimodal (voice/face)
- Full cultural module
- Dashboard UI
- Heavy RL / fine-tuning

---

## Compatibility

- Existing API keys and call shapes keep working.
- Unknown emotion labels from older models map carefully; prefer enum expansion over breaking renames.
- Evaluation without `felt_understood_score` from old prompts: default or recompute from overall when missing.

---

## Success criteria

- [ ] Python + TypeScript schemas include new fields
- [ ] Prompts request appraisal + felt_understood when relevant
- [ ] Memory stores salience; context builder uses it
- [ ] Unit/schema tests pass in CI
- [ ] Changelog + README mention v0.4 capabilities

---

## Suggested sequence

1. Models / Zod schemas  
2. Prompts (emotion + evaluation)  
3. Memory salience  
4. Tests  
5. Docs polish + release v0.4.0  

---

## Non-goals reminder

No claims of machine consciousness or therapy replacement.  
Uncertainty and safety remain mandatory.
