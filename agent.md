# NaviLearn Agent Guide

## Project
NaviLearn is a Streamlit app that recommends YouTube tutorials and playlists based on natural language queries.

## How to run
- Dev: `docker compose -f docker-compose.dev.yml up`
- Prod: `docker compose up`
- Local app entrypoint: `src/recommendation_ui.py`
- Stop dev with `docker compose -f docker-compose.dev.yml down`
- Stop prod with `docker compose down`

## Runtime files
- Cache file: `src/cache_store/search_cache.json`
- Log folder: `src/system_log/`

## Env rules
- Do not edit the real `.ENV` file unless the user explicitly asks.
- Use `src/.ENV.example` as the reference for expected variables.
- Required secrets:
  - `OPENAI_API_KEY`
  - `YOUTUBE_API_KEY`
- Safe defaults are handled in code for non-secret settings when possible.

## Git and Docker workflow
- Prefer editing source in `src/` and copying it in batch for prod images.
- Dev containers should rely on the bind mount from `docker-compose.dev.yml`.
- Keep generated cache and log files out of git.

## Code expectations
- Keep changes focused on the requested area.
- Prefer the existing cache objects in `src/caching.py`.
- Preserve the success/failure headers in tool return values.
- If you add new runtime files, make sure Docker and `.gitignore` stay aligned.

## Notes for future edits
- If a change affects persistence, update both load and save paths together.
- If a change affects tool output, keep the agent-facing format stable unless the user asks otherwise.
