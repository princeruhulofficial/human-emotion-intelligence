# Changelog

All notable changes to Human Emotion Intelligence (HEI) will be documented in this file.

## [0.2.0] - 2026-07-19

### Added
- **Emotional Memory**
  - Session-based emotion timeline
  - Automatic turn recording via `session_id`
  - Mood shift detection (improving / declining / intensifying / stabilizing)
  - Memory context injected into Strategy Planner
- **MCP Server** (Model Context Protocol)
  - Tools: `hei_analyze`, `hei_detect_emotion`, `hei_detect_intent`, `hei_get_mood_shift`, `hei_evaluate_response`
  - Optional token auth (`HEI_MCP_TOKEN`)
  - Rate limiting + structured logging
  - Compatible with Claude Desktop, Cursor, Windsurf
- **HTTP API** (API Gateway ready)
  - FastAPI server with `/v1/analyze`, `/v1/emotion`, `/v1/intent`, `/v1/evaluate`, `/v1/mood-shift`
  - Bearer / X-API-Key authentication
  - Rate limiting + CORS support
  - Ready for Nginx, Cloudflare, AWS API Gateway, Kong, Traefik
- New examples and documentation (`docs/mcp.md`, `docs/api-gateway.md`)

### Changed
- `HEI.analyze()` now accepts optional `session_id`
- Strategy Planner receives previous emotional context when available
- Version bumped to 0.2.0

## [0.1.1] - 2026-07-19

### Added
- Input validation, custom exceptions, ToneConfig model
- Timeout + max_retries on OpenAI client
- Golden set + validation tests
- TypeScript SDK with feature parity
- OpenRouter / any OpenAI-compatible endpoint support
- `improve_response()` with real retry loop

### Fixed
- Critical error handling and type safety issues

## [0.1.0] - 2026-07-19

### Added
- Initial MVP: Emotion, Intent, Strategy, Evaluation
- Python SDK + basic examples + PRD
