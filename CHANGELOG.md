# Changelog

All notable changes to Human Emotion Intelligence (HEI) will be documented in this file.

## [0.3.0] - Unreleased

### Added
- **TypeScript Emotional Memory** (full parity with Python)
- **Python memory unit tests**
- **GitHub Actions CI** (Python matrix + TypeScript typecheck/test/build)
- **Persistent Emotional Memory backends**
  - `memory` (default, in-process)
  - `sqlite` (zero-config file persistence)
  - `redis` (optional, multi-process)
  - `EmotionalMemory.from_env()` and `HEI(memory_backend=...)`
  - Docs: `docs/memory.md`

### Changed
- Package version → 0.3.0
- TypeScript SDK version → 0.3.0

## [0.2.0] - 2026-07-19

### Added
- Emotional Memory (Python, in-memory)
- MCP Server
- HTTP API (API Gateway ready)

## [0.1.1] - 2026-07-19

### Added
- Input validation, ToneConfig, TypeScript SDK, tests, OpenRouter support

## [0.1.0] - 2026-07-19

### Added
- Initial MVP
