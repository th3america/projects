# STARTFIRE 003 integration contract

Private STARTFIRE 003 is the canonical source for Greyfoot's portable operating files. It is not copied into this public repository.

Package ID: `greyfoot-startfire-003-20261120`.

Manifest entrypoints: `STARTFIRE.md`, `START-HERE.txt`, `startfire.py`, `AGENTS.md`.

The STARTFIRE 003 runner validates payload hashes, probes runtime/vault read-write, checks SQLite integrity, verifies required SELF records, generates `runtime/BOOT_PACKET.md`, checks Cortex learning-cluster, RIG-sync and AGI graph components, then writes bindings and a receipt. It supports `--portable` for a receiver-local vault.

## Linux receiver requirements
- Retrieve the complete payload and manifest through authorized Cloudmind transfer.
- Confirm every manifest path exists and every SHA-256 matches before running.
- Run with `--portable` on the new Contabo RIG unless an explicitly approved compatible vault is mounted.
- Do not blindly reuse Windows `source_vault` or `archive_routes` paths.
- Preserve source package; write receiver bindings and receipt locally.
- Review BOOT_PACKET, validation results and skipped checks. Hash success alone does not prove external archives exist.

STARTFIRE 003 wires/verifies the file-based memory, cortex and tool components it knows about. It does not install Ollama, create the new persistent PILOT runtime, implement browser automation, or prove autonomous orchestration. SEEDFIRE builds those layers separately.
