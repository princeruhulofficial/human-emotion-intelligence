# Changelog

All notable changes to Human Emotion Intelligence (HEI) will be documented in this file.

## [0.3.0] - Unreleased

### Added
- **TypeScript Emotional Memory** (full parity with Python)
  - `EmotionalMemory` class
  - `analyze(message, sessionId?)` support
  - `getMoodShift()`, timeline, context-for-strategy
  - Unit tests with Vitest
- **Python memory unit tests** (`tests/test_memory.py`)
- **GitHub Actions CI**
  - Python 3.10 / 3.11 / 3.12 matrix
  - TypeScript typecheck + tests + build
  - Unit tests run without API keys

### Changed
- TypeScript SDK version → 0.3.0

## [0.2.0] - 2026-07-19

### Added
- **Emotional Memory** (Python)
  - Session-based emotion timeline
  - Automatic turn recording via `session_id`
  - Mood shift detection
  - Memory context injected into Strategy Planner
- **MCP Server** (Model Context Protocol)
  - Tools + optional token auth + rate limiting
- **HTTP API** (API Gateway ready)
  - FastAPI with Bearer / X-API-Key auth

## [0.1.1] - 2026-07-19

### Added
- Input validation, custom exceptions, ToneConfig
- TypeScript SDK (initial)
- Golden set + validation tests
- OpenRouter support

## [0.1.0] - 2026-07-19

### Added
- Initial MVP: Emotion, Intent, Strategy, Evaluation
- Python SDK + PRD
