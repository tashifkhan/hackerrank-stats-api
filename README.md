# HackerRank Stats API

A FastAPI + `uv` port of the original LeetCode Stats API, adapted for public HackerRank profiles.

## Features

- Same route surface as the source project
- FastAPI app with Swagger at `/docs`
- Public HackerRank profile, badge, contest, score, recent challenge, and submission-history adapters
- Heatmap endpoint compatible with the LeetCode API response shape
- Root dashboard for quick username lookups

## API Endpoints

### Get User Statistics

```text
GET /{username}
```

Returns a LeetCode-compatible stats payload using public HackerRank data. Some LeetCode-specific fields, such as difficulty totals and acceptance rate, are not exposed by HackerRank and remain `0` for compatibility.

### Get Contest Rankings

```text
GET /{username}/contests
```

Returns public contest participation history and derived contest summary values when available.

### Get User Profile

```text
GET /{username}/profile
```

Returns public profile info, score-derived contribution values, badges, submission history, and recent challenges.

### Get Contribution Heatmap Data

```text
GET /{username}/heatmap
```

Returns normalized daily contribution data from HackerRank submission history.

### Get User Badges

```text
GET /{username}/badges
```

Returns public badges and an inferred active badge.

## Installation

```bash
uv sync
```

## Run Locally

```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 58352
```

Then open:

- `http://localhost:58352/`
- `http://localhost:58352/docs`

## Tests

```bash
uv run python -m unittest discover -s tests
```

## Notes

- The API is built on public HackerRank endpoints.
- Route names and top-level response envelopes mirror the original LeetCode project.
- Where HackerRank does not publish an exact LeetCode equivalent, the response keeps the field for compatibility and either derives a value from public score data or leaves it at the neutral default.
