# Changelog

All notable changes to Human Emotion Intelligence (HEI) will be documented in this file.

## [0.4.0] - Unreleased

### Added
- **Research docs:** `docs/research-insights-2026.md`, `docs/roadmap-v0.4.md`
- **Plutchik-aligned emotion taxonomy** (trust, disgust, surprise, anticipation, love, optimism, disappointment, burnout, …)
- **AppraisalSignals** (optional): goal_relevance, coping_potential, agency
- **`felt_understood_score`** on EvaluationResult (primary product metric)
- **Memory salience** per turn + salience-aware strategy context

### Changed
- Polarity maps expanded for mood-shift detection
- TypeScript schemas kept in parity with Python models

## [0.3.0] - 2026-07-23

### Added
- TypeScript Emotional Memory
- Persistent backends (SQLite / Redis)
- GitHub Actions CI
- Zod golden parse tests + SEO README

## [0.2.0] - 2026-07-19

### Added
- Emotional Memory (Python), MCP Server, HTTP API

## [0.1.0] - 2026-07-19

### Added
- Initial MVP
