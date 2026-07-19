# Changelog

All notable changes to Human Emotion Intelligence (HEI) will be documented in this file.

## [0.1.1] - 2026-07-19

### Added
- Proper input validation (empty, null, too long messages)
- Custom exceptions: `HEIError`, `HEIValidationError`
- `ToneConfig` model (replaces raw dict)
- Timeout + max_retries support on OpenAI client
- Golden set integration tests (`tests/test_golden.py`)
- Validation unit tests (`tests/test_validation.py`)
- TypeScript SDK with full feature parity
- OpenRouter / any OpenAI-compatible endpoint support
- `improve_response()` with real retry loop

### Fixed
- Critical: No error handling on LLM calls
- Critical: Weak typing on tone configuration
- Critical: TypeScript `any` usage reduced
- `improve_response` now respects `max_attempts` properly

### Changed
- Better prompts for emotion, strategy and evaluation
- More defensive JSON parsing

## [0.1.0] - 2026-07-19

### Added
- Initial MVP
- Emotion Detection (primary + secondary + hidden + intensity)
- Emotional Intent Detection
- Response Strategy Planner
- Response Evaluation + Rewrite
- Python SDK
- Basic examples and PRD
