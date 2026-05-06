# HackerRank Stats API

A FastAPI + `uv` service for exploring public HackerRank profiles, stats, and activity.

Live dashboard at the root route (`/`) — enter any public HackerRank username to get a full profile view with heatmap, badges, recent submissions, and contest history.

## API Endpoints

All endpoints accept a public HackerRank username and return JSON.

### `GET /{username}`

Aggregated stats: total solved, best ranking, reputation, contribution points, and submission calendar.

```json
{
  "status": "success",
  "totalSolved": 70,
  "ranking": 1,
  "contributionPoints": 5,
  "reputation": 0,
  "submissionCalendar": {}
}
```

### `GET /{username}/profile`

Full profile: avatar, real name, country, company, school, skill tags, bio, social links, badges, recent submissions, and per-track submission stats.

### `GET /{username}/heatmap`

Daily contribution heatmap built from submission history, including current streak, longest streak, active days, and per-day activity levels (0–4).

> Note: HackerRank's public submission history endpoint may return empty data for some profiles even when activity exists.

### `GET /{username}/badges`

Awarded badges and the inferred active badge (highest stars/level).

### `GET /{username}/contests`

Contest participation history, rating, global ranking, and top percentile. Returns an empty history for users with no contest participation.

## Running Locally

```bash
uv sync
uv run uvicorn main:app --reload --host 0.0.0.0 --port 58352
```

Open:
- `http://localhost:58352/` — visual profile dashboard
- `http://localhost:58352/docs` — Swagger UI

## Testing

```bash
# Quick smoke test with a known public profile
curl http://localhost:58352/shauryarahlon_10

# Run unit tests
uv run python -m unittest discover -s tests
```

## Notes

- All data comes from public HackerRank endpoints — no authentication required.
- Fields that HackerRank does not expose publicly are derived from score data or default to neutral values.
- Difficulty breakdown (easy/medium/hard) and acceptance rate are not available from public HackerRank data and will always be `0`.
