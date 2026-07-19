# HEI HTTP API + API Gateway Integration

HEI can run as a production-ready HTTP service using FastAPI.  
You can put it behind any API Gateway (Kong, AWS API Gateway, Nginx, Cloudflare, Traefik, etc.).

## Quick Start

```bash
pip install -e ".[api]"   # or: pip install fastapi uvicorn

export OPENAI_API_KEY=sk-...
export HEI_API_TOKEN=your-secret-token     # recommended
export HEI_MODEL=gpt-4o-mini

uvicorn hei.api:app --host 0.0.0.0 --port 8000
```

Open docs: http://localhost:8000/docs

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/v1/analyze` | Full Emotion + Intent + Strategy |
| `POST` | `/v1/emotion` | Emotion only |
| `POST` | `/v1/intent` | Intent only |
| `GET` | `/v1/mood-shift/{session_id}` | Mood shift for a session |
| `POST` | `/v1/evaluate` | Evaluate a generated response |

## Authentication

If `HEI_API_TOKEN` is set, every request (except `/health`) must include one of:

```http
Authorization: Bearer your-secret-token
```

or

```http
X-API-Key: your-secret-token
```

## Example Requests

### Analyze

```bash
curl -X POST http://localhost:8000/v1/analyze \
  -H "Authorization: Bearer your-secret-token" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I guess my startup is over.",
    "session_id": "user_123"
  }'
```

### Emotion only

```bash
curl -X POST http://localhost:8000/v1/emotion \
  -H "Authorization: Bearer your-secret-token" \
  -H "Content-Type: application/json" \
  -d '{"message": "I\'m fine."}'
```

## Putting Behind an API Gateway

### Nginx example

```nginx
server {
    listen 80;
    server_name hei.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### AWS API Gateway

1. Create an HTTP API
2. Add a reverse proxy / VPC link to your HEI service
3. Optionally add API Gateway API Keys + Usage Plans for extra rate limiting
4. Forward `Authorization` header to the upstream

### Cloudflare / Kong / Traefik

Just point the upstream to `http://hei-service:8000` and enable:

- TLS termination
- Rate limiting
- IP allow-listing (if needed)
- Header forwarding (`Authorization`, `X-API-Key`)

## Environment Variables

| Variable | Description | Default |
|----------|-------------|--------|
| `OPENAI_API_KEY` | LLM provider key | required |
| `HEI_API_TOKEN` | Protects the HTTP API | off |
| `HEI_API_RATE_LIMIT` | Requests per minute per token | 120 |
| `HEI_CORS_ORIGINS` | Allowed CORS origins | `*` |
| `HEI_MODEL` | Model name | `gpt-4o-mini` |
| `HEI_HOST` | Bind host | `0.0.0.0` |
| `HEI_PORT` | Bind port | `8000` |

## Production Checklist

- [ ] Set a strong `HEI_API_TOKEN`
- [ ] Run behind HTTPS (Gateway or reverse proxy)
- [ ] Enable Gateway-level rate limiting as a second layer
- [ ] Do not expose the raw port publicly without auth
- [ ] Use a process manager (systemd, Docker, Kubernetes)
- [ ] Monitor `/health`
