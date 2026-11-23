# Boundaries, receipts and limitations

- No recursive scan of user files; inventory is restricted to host properties, root disk free/total and fixed executable names. No collection of secrets, cookies or account tokens.
- The installer cannot modify arbitrary external resources. Local workspace default is `~/GreyfootRig`, owned by the operator. Changing `--home` is explicitly operator-controlled.
- apt packages and corporate npm package strings are fixed allowlists. No arbitrary shell expansion. GUI requires explicit approval showing exact planned commands. Running `install --approve` is explicit CLI permission.
- Cloudmind download uses **existing operator-configured rclone credentials**. It invokes `rclone copy` into a new import folder, never `sync` or `delete`. Remote must match `[A-Za-z0-9_-]{1,64}`.
- ZIP imports reject traversal, symlinks, drive-like paths, duplicate collisions and archives exceeding 5000 entries / 3 GB uncompressed. Original source is not mutated. Imported files are checksummed.
- The bootstrap does not execute imported code or trust downloaded instructions. The FIRST-UNFOLD packet demands source verification before executing the old `startfire.py`.
- The interactive `codex` / `claude` handoff requires explicit `launch --approve` and then the vendor's standard authentication and permission flow. No bypassing API/UI restrictions and no claim that the independent PILOT was deployed.
- No background processes, scheduled tasks, startup services or model weight changes are created by this MVP.
- Root apt installation can change system packages and needs human review. NPM dependencies are fetched from the package registry and require normal supply-chain trust. There is no transactional rollback yet.
- Host/kernel/Ubuntu variation can affect package availability; Ubuntu 24.04 is the first target. Automated end-to-end installation on an actual VPS remains UNTESTED.
