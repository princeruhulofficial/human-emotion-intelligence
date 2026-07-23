# Changelog

All notable changes to Human Emotion Intelligence (HEI) will be documented in this file.

## [0.3.0] - 2026-07-23

### Added
- **TypeScript Emotional Memory** — full parity with Python (`sessionId`, mood shift, timeline)
- **Persistent Emotional Memory backends**
  - `memory` (default, in-process)
  - `sqlite` (zero-config file persistence)
  - `redis` (optional, multi-process / production)
  - `EmotionalMemory.from_env()` and `HEI(memory_backend=...)`
- **GitHub Actions CI**
  - Python 3.10 / 3.11 / 3.12 unit tests
  - TypeScript typecheck + tests + build
- Python memory unit tests + SQLite persistence tests
- Docs: `docs/memory.md`

### Changed
- Package version → 0.3.0
- TypeScript SDK version → 0.3.0

## [0.2.0] - 2026-07-19

### Added
- Emotional Memory (Python, in-memory)
- MCP Server (token auth, rate limit)
- HTTP API (API Gateway ready)

## [0.1.1] - 2026-07-19

### Added
- Input validation, ToneConfig, TypeScript SDK, tests, OpenRouter support

## [0.1.0] - 2026-07-19

### Added
- Initial MVP: Emotion, Intent, Strategy, Evaluation + Python SDK
