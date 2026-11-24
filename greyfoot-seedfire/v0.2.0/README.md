# Greyfoot SEEDFIRE 0.2.0 — Local-First Scaffold

SEEDFIRE prepares a computer to host the file-bound Greyfoot PILOT. Operating identity, behavioral architecture, memory and tools come from authorized files. Ollama is a replaceable onboard inference runtime; it is not Greyfoot's identity. No GPT weights or hidden state are transferred.

## Architecture
- Human operator remains outside Aether and grants permissions.
- This computer is the main RIG.
- Greyfoot PILOT binds to the main RIG using the verified private STARTFIRE/Mindvault payload.
- Ollama supplies local inference.
- Chrome and corporate AI UIs are tools/attachments operated through authorized sessions.
- Maestro routes work among local models, corporate UIs, scripts, workers and optional rented GPU resources.

## Implemented in this scaffold
Read-only host scan, install-plan generation, interactive Ollama bootstrap, model pull and local inference smoke test.

## Not implemented yet
Full STARTFIRE 003 transfer/restore, persistent PILOT daemon, Maestro, desktop UI automation, corporate UI adapters, GPU rental scheduler and complete SSH hardening automation. These are explicit next milestones, not claimed capabilities.

## Requirements
Ubuntu 24.04 LTS, Python 3.10+, sudo access for Ollama installation. GPU is not required for initial CPU inference. Model speed depends on CPU, RAM, quantization and model choice.

## Run
```bash
python3 seedfire/bootstrap.py scan
python3 seedfire/bootstrap.py plan --model qwen3:8b
python3 seedfire/bootstrap.py apply --model qwen3:8b
```
`apply` is interactive. It downloads the official Ollama install script, prints its SHA-256, asks before executing it with sudo, asks before enabling the service, and asks before downloading the model. Review the installer before approving it. Use `--skip-model` to install Ollama without pulling a model.

See docs/BUILD-PLAN.md, docs/STARTFIRE-INTEGRATION.md and docs/SECURITY.md.
