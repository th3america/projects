# 🐾 Greyfoot SEEDFIRE — Machine Scan → Approval → First Unfold

A **working, conservative Python 3.10+ MVP** for preparing a Linux computer as Greyfoot's **main RIG**. It uses an optional Tkinter desktop interface or a headless command line. It does not claim to be a completed persistent AI operating system.

**Frozen topology:** Human operator **outside Aether** ⇄ **computer (main RIG, containing Greyfoot PILOT)** ⇄ **attachments** (Chrome, corporate AI RIG interfaces, Docker workers, local LLMs, Cloudmind, other tools). The corporate AI RIG is a *bootstrap reasoning attachment*, not the home of Greyfoot.

## Start

On a Linux desktop with Python and Tk installed:

```bash
chmod +x run.sh
./run.sh
```

On a headless cloud server:

```bash
python3 seedfire.py scan
python3 seedfire.py plan --rig codex --extras git,sqlite,unzip,rclone
```

`scan` discovers OS, CPU threads, RAM, root filesystem size, graphical session and a fixed inventory of executable tools. **No recursive user-file scans, secret reads or network transmission.** `plan` calculates an install list without modifying the system.

### Installation (explicit consent)

```bash
python3 seedfire.py install --rig codex --extras git,sqlite,unzip,rclone
# REVIEW THE PRINTED PLAN FIRST (dry run exits 2)
python3 seedfire.py install --rig codex --extras git,sqlite,unzip,rclone --approve
```

Ubuntu/Debian apt installs only from a fixed allowlist. The selected corporate CLI installs from an exact official npm package into `~/GreyfootRig/toolchain`, avoiding root npm installs. Selected Codex / Claude authentication remains interactive. For Antigravity, use the [official Linux installer](https://antigravity.google/download/linux) (not automatically fetched).

To run the one-window desktop sequence: select first RIG and optional components → **GO Scan + Plan** → **Approve + Install** → **Import / Cloudmind Fetch** → **Prepare UNFOLD**. The GUI is a bootstrap panel; Chrome remains a tool, not Greyfoot's permanent interface.

### Bring in our existing STARTFIRE v2

From a ZIP/folder you obtained from Cloudmind:

```bash
python3 seedfire.py import --source ~/Downloads/Greyfoot-Startfire-002.zip
```

Or configure your own Google Drive remote with `rclone config` and use its remote name; SEEDFIRE copies only the known `Greyfoot-Startfire-002` source folder into its local imports (never deletes anything in Drive):

```bash
python3 seedfire.py cloudmind --remote cloudmind --approve
```

Cloudmind source: [Greyfoot-Startfire-002](https://drive.google.com/drive/folders/18KyUUGYMXt0iUlzouY17okVH9qPMs3EB). This MVP does **not** ship those personal data files, credentials, or a fabricated cloud-mapped copy. It imports them from a user-authorized source and writes SHA-256 receipts for the copy. The imported STARTFIRE `manifest.json` must be verified by the bootstrap agent before its `startfire.py` runs.

### First UNFOLD handoff

```bash
python3 seedfire.py unfold --rig codex
cat ~/GreyfootRig/FIRST-UNFOLD.md
python3 seedfire.py launch --rig codex            # dry run; no AI invoked
python3 seedfire.py launch --rig codex --approve  # interactive CLI prompt handoff
```

The launch selects an installed `codex` or `claude` binary, passes the **FIRST-UNFOLD** text as its initial interactive prompt, and leaves the human at the console for normal account sign-in/tool approvals. It does *not* bypass vendor controls, scrape UI sessions or launch unattended loops. Antigravity requires manual opening and pasting the generated packet.

## Safety / scope

- **SELF**: Pilot identity/anchors, on-RIG working files, verified operational procedures. **NOT-SELF**: unrelated user/system files, other accounts, services or machines.
- Read-only scan by default. System changes require a separately reviewed plan and user consent. No arbitrary shell commands from remote manifests are executed.
- The bootstrap creates files only below `~/GreyfootRig` (or explicit `--home`), except approved apt/npm installations. It records receipts and avoids uploading host inventories anywhere.
- External Cloudmind authorization is set up by the operator; no OAuth tokens or passwords stored by SEEDFIRE.
- An AI launch does not mean a persistent independent PILOT exists. The FIRST-UNFOLD packet asks the chosen RIG to build, test and receipt that next stage.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Project status

**v0.1.0 MVP** — Linux local inspection, install planning, explicitly approved package installation, portable ZIP/folder import, optional Cloudmind rclone copy, receipt generation, FIRST-UNFOLD packet and interactive corporate CLI handoff. **Not implemented:** model-independent resident PILOT daemon, autonomous UI operation, full Cortex/Mindvault validation or recovery/rollback, GPU benchmarking, unattended cloud configuration. They require separate verified development.

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) and [SECURITY.md](docs/SECURITY.md).
