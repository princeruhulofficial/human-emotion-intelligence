# Changelog

All notable changes to Human Emotion Intelligence (HEI) will be documented in this file.

## [0.2.0] - 2026-07-19

### Added
- **Emotional Memory** (major feature)
  - Session-based emotion timeline
  - Automatic turn recording when `session_id` is provided
  - Mood shift detection (improving / declining / intensifying / stabilizing)
  - Memory context injected into Strategy Planner
  - `hei.memory.get_timeline()`, `detect_mood_shift()`, `get_context_for_strategy()`
- New example: `examples/memory_example.py`

### Changed
- `HEI.analyze()` now accepts optional `session_id`
- Strategy Planner can receive previous emotional context

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
