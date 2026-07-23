# Emotional Memory

HEI can remember emotional context across turns in a conversation.

## Backends

| Backend | Persist after restart? | Multi-process? | Dependency |
|---------|------------------------|----------------|------------|
| `memory` (default) | No | No | None |
| `sqlite` | Yes | Limited* | None (stdlib) |
| `redis` | Yes | Yes | `pip install redis` |

\* SQLite works across processes on the same machine with WAL mode, but Redis is better for distributed setups.

## Quick Start

### In-memory (default)

```python
from hei import HEI

hei = HEI(api_key="sk-...")
hei.analyze("I failed my startup.", session_id="user_1")
hei.analyze("Trying to stay positive.", session_id="user_1")

print(hei.get_mood_shift("user_1").summary)
```

### SQLite (recommended for single-server persistence)

```bash
export HEI_MEMORY_BACKEND=sqlite
export HEI_MEMORY_PATH=./data/hei_memory.db
```

```python
from hei import HEI
from hei.memory import EmotionalMemory

hei = HEI(api_key="sk-...", memory=EmotionalMemory.from_env())
# or
hei = HEI(api_key="sk-...", memory_backend="sqlite")
```

After process restart, the same `session_id` still has its timeline.

### Redis

```bash
pip install redis
export HEI_MEMORY_BACKEND=redis
export HEI_REDIS_URL=redis://localhost:6379/0
```

```python
hei = HEI(api_key="sk-...", memory_backend="redis")
```

## API

```python
hei.memory.get_timeline(session_id)
hei.memory.detect_mood_shift(session_id)
hei.memory.get_context_for_strategy(session_id)
hei.memory.clear_session(session_id)
hei.get_mood_shift(session_id)
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|--------|
| `HEI_MEMORY_BACKEND` | `memory` / `sqlite` / `redis` | `memory` |
| `HEI_MEMORY_PATH` | SQLite file path | `hei_memory.db` |
| `HEI_REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
