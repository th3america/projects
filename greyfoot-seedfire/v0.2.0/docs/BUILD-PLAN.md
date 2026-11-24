# SEEDFIRE build plan

## Phase 0 — Bootstrap (this scaffold)
- Read-only inventory of CPU, RAM, disk, GPU and commands.
- Generate a plan before changes.
- Install Ollama only after explicit approval.
- Pull a selectable local model and run an inference smoke test.

## Phase 1 — Restore Greyfoot's file-bound architecture
- Retrieve private STARTFIRE 003 payload from Cloudmind through operator-authorized transfer.
- Verify every manifest entry before activation.
- Run STARTFIRE portable mode and inspect receipt and boot packet.
- Keep source Mindvault immutable; create a receiver-local working copy.
- Verify SQLite integrity, ledger chain, SELF anchors, Cortex graph, learning cluster and cross-RIG sync DB.
- Resolve source paths/archive routes explicitly; Windows paths are not assumed to exist on Linux.

## Phase 2 — Local PILOT runtime
- Persistent local runtime loads SELF/behavioral anchors from files and invokes Ollama locally.
- Separate identity/configuration, inference provider, memory, tools and orchestration.
- Replace models without changing identity or memory.
- Add health checks, restart policy, bounded context assembly and receipts.

## Phase 3 — Main RIG control plane
- Local operator interface for tasks, permissions, run state and receipts.
- Tool registry, capability declarations, worker lifecycle and resource limits.
- Docker isolation where appropriate; benchmark CPU, RAM and VRAM independently.

## Phase 4 — Aetherbridge and corporate UI attachments
- Adapters for authenticated, user-authorized browser sessions.
- Chrome is a tool; local PILOT interface remains primary.
- Visible UI automation with session boundaries and approval for consequential actions.
- Do not bypass MFA, CAPTCHAs, access controls, subscription limits or provider restrictions.
- Never scrape/store passwords; use user-managed authenticated browser profiles.

## Phase 5 — Optional GPU workers
- Provider-neutral inference worker interface.
- Provision only after approval; record compute, storage and bandwidth separately.
- Return results to main RIG; destroy ephemeral workers only after verifying persistence.

## Acceptance gates
1. Bootstrap works on clean Ubuntu 24.04.
2. Ollama local API responds and smoke test succeeds.
3. STARTFIRE payload verifies without mutating source.
4. Local PILOT starts without corporate AI session.
5. Memory and receipts survive restart.
6. Corporate UI attachment works through authorized session and disconnects safely.
7. Local tasks work with all corporate sessions closed.
