# ADR 0003: Click CLI, uv Packaging, and Optional LiteLLM Interpretation

## Status

Accepted.

## Context

The Milestone 1 CLI was argparse, project metadata had no build backend, and the ChatGPT adapter only read a directory that contained `conversations.json` with string message parts.

Real ChatGPT data exports are often a zip, a single JSON file, or split `conversations-*.json` files. Messages use unix timestamps and mix text with image pointers, code, and user-context fields. A world produced from that export must validate.

The charter uses models for semantic extraction and keeps parsing deterministic. An Ollama server on the local network is the intended model host.

## Decision

- Replace the CLI with Click. Command names and arguments stay compatible with the Milestone 1 surface.
- Package the app with uv and the hatchling build backend. `click` and `litellm` are runtime dependencies. `uv.lock` is the lockfile.
- Accept a ChatGPT directory, a conversation JSON file, or a zip export, including split conversation files and a top-level `{"conversations": [...]}` document. Keep text from string parts, text fields, code, and user context. Skip image-only parts. Store timestamps as UTC date-times. Store author role and conversation title when the export provides them.
- Keep model use optional. With no model configured, ingestion does not contact a network. When `--model` or `WORLDGEN_MODEL` is set, LiteLLM requests candidate entities and assertions. `--model-api-base`, `WORLDGEN_MODEL_API_BASE`, or `OLLAMA_API_BASE` selects the server, so a network Ollama endpoint is addressed with a model name such as `ollama/llama3.1`.
- Store model output as candidate or conflicting assertions with `interpretation_level=interpretation`. Do not accept those assertions automatically. Skip a repeat call for the same model and API base while the source hash is unchanged.
- Omit `valid_until` when a claim has no end time. The assertion schema accepts a date-time string and rejects null.

## Rationale

- Click is the command interface the package script can call directly, and it keeps the existing subcommands.
- uv is already the documented package manager. A hatchling backend is what `uv build` needs to produce an installable wheel.
- Export parsing is deterministic infrastructure. Semantic extraction is the point where a model is justified, and it has to be explicit.
- LiteLLM speaks the Ollama OpenAI-compatible API without binding the world format to one provider.

## Consequences

### Positive

- `uv sync` and `uv build` install and package the app.
- A real ChatGPT export can be ingested, validated, and indexed without a model.
- A network Ollama server can be targeted when interpretation is requested.

### Tradeoffs

- LiteLLM is installed even when interpretation is not used.
- The first completed interpretation for a source and model is kept. A later model reply is not fetched until the source bytes change.
- This does not implement the other planned model-assisted recipes.

## Relationship to earlier decisions

This does not replace ADR 0001. Default ingestion remains deterministic, content-hashed, and provenance-linked. Model output is labeled interpretation and stays reviewable.
