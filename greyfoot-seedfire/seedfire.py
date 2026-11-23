#!/usr/bin/env python3
"""SEEDFIRE: inspect, approve, stage and ignite a Greyfoot RIG. Python 3.10+ stdlib."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

VERSION = "0.1.0"
DEFAULT_HOME = Path.home() / "GreyfootRig"
RIGS = {"codex": ("codex", "@openai/codex"), "claude": ("claude", "@anthropic-ai/claude-code"), "antigravity": ("antigravity", None), "none": (None, None)}
EXTRAS = {"docker": "docker.io", "sqlite": "sqlite3", "git": "git", "curl": "curl", "unzip": "unzip", "desktop": "xfce4", "tk": "python3-tk", "rclone": "rclone"}
CLOUDMIND_SUBPATH = "Greyfoot🐾/Greyfoot Mindvault/toolshed/agents/Greyfoot-Startfire-002"
MAX_ZIP_ENTRIES = 5000
MAX_UNCOMPRESSED = 3_000_000_000


def timestamp() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def jwrite(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)
    return path


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def os_release() -> dict:
    result = {}
    try:
        for line in Path("/etc/os-release").read_text().splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                result[k] = v.strip('"')
    except OSError:
        pass
    return result


def memory_mib() -> int | None:
    try:
        raw = Path("/proc/meminfo").read_text()
        match = re.search(r"^MemTotal:\s+(\d+)\s+kB", raw, re.M)
        return int(match.group(1)) // 1024 if match else None
    except OSError:
        return None


def scan() -> dict:
    """Host/tool inventory only: no user-file traversal, credential reads or network calls."""
    root = shutil.disk_usage("/")
    toolnames = ("python3", "git", "curl", "unzip", "sqlite3", "docker", "ollama", "rclone", "node", "npm", "codex", "claude", "antigravity", "startxfce4", "lspci", "nvidia-smi", "pkexec", "apt-get")
    found = {k: shutil.which(k) for k in toolnames}
    # Do not collect environment variables, tokens, personal files or account data.
    return {
        "schema": "seedfire.scan.v1", "version": VERSION, "time_utc": timestamp(),
        "os": os_release(), "kernel": platform.release(), "arch": platform.machine(),
        "cpu_threads": os.cpu_count(), "ram_mib": memory_mib(),
        "root_disk_total_gib": round(root.total / 2**30, 2),
        "root_disk_free_gib": round(root.free / 2**30, 2),
        "graphical_session": bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")),
        "tools": found, "scope": "machine inventory only; no content scan, no outbound traffic",
    }


def plan(report: dict, rig: str = "codex", extras: tuple[str, ...] = ()) -> dict:
    if rig not in RIGS:
        raise ValueError(f"Unknown RIG: {rig}")
    for x in extras:
        if x not in EXTRAS:
            raise ValueError(f"Unknown extra: {x}")
    have = report["tools"]
    apt = []
    for x in extras:
        checked = {"sqlite": "sqlite3", "desktop": "startxfce4"}.get(x, x)
        if x == "tk":
            try:
                import tkinter  # noqa: F401
                present = True
            except ImportError:
                present = False
        else:
            present = bool(have.get(checked))
        if not present:
            pkg = EXTRAS[x]
            if pkg not in apt:
                apt.append(pkg)
    binary, npm_pkg = RIGS[rig]
    if npm_pkg and not have.get(binary):
        if not have.get("node"):
            apt.append("nodejs")
        if not have.get("npm"):
            apt.append("npm")
    if rig == "antigravity" and not have.get("antigravity"):
        manual = "Install from https://antigravity.google/download/linux and authenticate in the app"
    else:
        manual = "Authenticate your chosen corporate RIG interactively; no passwords/tokens stored"
    apt = sorted(set(apt))
    return {
        "schema": "seedfire.plan.v1", "rig": rig, "extras": list(extras),
        "apt_packages": apt,
        "npm_package": npm_pkg if npm_pkg and not have.get(binary) else None,
        "manual": manual,
        "commands": (["sudo apt-get update", "sudo apt-get install -- " + " ".join(apt)] if apt else [])
                    + ([f"npm install --prefix <GREYFOOT_RIG>/toolchain {npm_pkg}"] if npm_pkg and not have.get(binary) else []),
        "requires_approval": True,
        "cloudmind": "import existing STARTFIRE v2 from a local copy or authorized rclone remote",
        "note": "No installations, authentication or source imports have occurred.",
    }


def approved_install(spec: dict, home: Path, runner=subprocess.run) -> list[dict]:
    """Only execute fixed allowlisted package commands after explicit approval."""
    allowed = set(EXTRAS.values()) | {"nodejs", "npm"}
    pkgs = spec["apt_packages"]
    if not set(pkgs).issubset(allowed):
        raise ValueError("Non-allowlisted apt package refused")
    npm_package = spec["npm_package"]
    if npm_package not in (None, "@openai/codex", "@anthropic-ai/claude-code"):
        raise ValueError("Non-allowlisted npm package refused")
    steps = []
    if pkgs:
        if not shutil.which("apt-get"):
            raise RuntimeError("apt-get unavailable: Ubuntu/Debian installation required")
        prefix = [] if os.geteuid() == 0 else ["sudo"]
        for cmd in (prefix + ["apt-get", "update"], prefix + ["apt-get", "install", "-y", "--"] + pkgs):
            result = runner(cmd, check=False)
            steps.append({"cmd": cmd, "exit_code": result.returncode})
            if result.returncode:
                raise RuntimeError(f"Install step failed ({result.returncode}): {cmd}")
    if npm_package:
        if not shutil.which("npm"):
            raise RuntimeError("npm not installed; install Node/npm, then retry")
        prefix = home / "toolchain"
        prefix.mkdir(parents=True, exist_ok=True)
        cmd = ["npm", "install", "--no-audit", "--no-fund", "--prefix", str(prefix), npm_package]
        result = runner(cmd, check=False)
        steps.append({"cmd": cmd, "exit_code": result.returncode})
        if result.returncode:
            raise RuntimeError(f"NPM install failed ({result.returncode})")
    return steps


def safe_unpack_zip(source: Path, destination: Path) -> list[Path]:
    """Reject traversal, links, oversized archives; never overwrite a preexisting import."""
    if destination.exists():
        raise FileExistsError(f"Import already exists: {destination}")
    destination.mkdir(parents=True)
    imported = []
    try:
        with zipfile.ZipFile(source) as zf:
            items = zf.infolist()
            if len(items) > MAX_ZIP_ENTRIES or sum(i.file_size for i in items) > MAX_UNCOMPRESSED:
                raise ValueError("Archive exceeds SEEDFIRE import limits")
            for info in items:
                if (info.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError("Archive contains symlink")
                name = info.filename.replace("\\", "/")
                parts = Path(name).parts
                if not name or name.startswith("/") or not parts or any(p in ("..", ".") for p in parts) or ":" in parts[0]:
                    raise ValueError(f"Unsafe archive entry: {name}")
                target = destination.joinpath(*parts)
                if info.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(info) as src, target.open("xb") as out:
                        shutil.copyfileobj(src, out)
                    imported.append(target)
    except BaseException:
        shutil.rmtree(destination, ignore_errors=True)
        raise
    return imported


def import_source(source: Path, home: Path) -> dict:
    source = source.expanduser().resolve(strict=True)
    folder = home / "imports" / timestamp()
    # A source that encloses the output would recursively copy its own new files.
    if source.is_dir() and (folder.resolve() == source or source in folder.resolve().parents):
        raise ValueError("Source directory contains destination; choose a different source")
    if folder.exists():
        raise FileExistsError(folder)
    if source.is_file() and source.suffix.lower() == ".zip":
        copied = safe_unpack_zip(source, folder)
    elif source.is_dir():
        # Do not follow directory symlinks or copy special files.
        for p in source.rglob("*"):
            if p.is_symlink():
                raise ValueError("Source contains symlink; aborting")
        folder.mkdir(parents=True)
        copied = []
        try:
            for p in source.rglob("*"):
                relative = p.relative_to(source)
                target = folder / relative
                if p.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                elif p.is_file():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(p, target)
                    copied.append(target)
                else:
                    raise ValueError("Source contains special file")
        except BaseException:
            shutil.rmtree(folder, ignore_errors=True)
            raise
    else:
        raise ValueError("Source must be a folder or .zip")
    index = {str(p.relative_to(folder)): digest(p) for p in copied}
    receipt = {"schema": "seedfire.import.v1", "source": str(source), "dest": str(folder), "files": index, "time_utc": timestamp()}
    jwrite(home / "receipts" / f"import-{timestamp()}.json", receipt)
    return receipt


def cloudmind_fetch(remote: str, home: Path, runner=subprocess.run) -> dict:
    """Copy known STARTFIRE package using preconfigured rclone remote; never mirror/delete."""
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", remote):
        raise ValueError("Remote name must be alphanumeric, dash or underscore")
    if not shutil.which("rclone"):
        raise RuntimeError("rclone not installed/configured")
    dest = home / "imports" / ("cloudmind-" + timestamp())
    if dest.exists():
        raise FileExistsError(dest)
    dest.mkdir(parents=True)
    src = f"{remote}:{CLOUDMIND_SUBPATH}"
    cmd = ["rclone", "copy", src, str(dest), "--exclude", ".git/**"]
    result = runner(cmd, check=False)
    if result.returncode:
        raise RuntimeError(f"Cloudmind download failed ({result.returncode}); partial files at {dest}")
    files = sorted(x for x in dest.rglob("*") if x.is_file())
    receipt = {"schema": "seedfire.cloudmind.v1", "remote": remote, "dest": str(dest),
               "files": {str(x.relative_to(dest)): digest(x) for x in files}, "time_utc": timestamp()}
    jwrite(home / "receipts" / f"cloudmind-{timestamp()}.json", receipt)
    return receipt


def unfold(home: Path, rig: str, source_dir: Path | None = None) -> Path:
    """Stage the first command, not a claim that the target model was loaded."""
    home.mkdir(parents=True, exist_ok=True)
    report = scan()
    jwrite(home / "receipts" / "latest-scan.json", report)
    loc = str(source_dir.resolve()) if source_dir else "NOT BOUND — import the STARTFIRE v2 package first"
    prompt = f"""# GREYFOOT SEEDFIRE — FIRST UNFOLD COMMAND

You are the chosen BOOTSTRAP reasoning RIG ({rig}), not Greyfoot's permanent main RIG.
The HUMAN operator is OUTSIDE Aether. The cloud COMPUTER is the MAIN RIG.
PILOT GREYFOOT resides WITHIN that computer and orchestrates attachments.
Chrome, corporate AI interfaces, models, containers, Cloudmind and other systems are ATTACHMENTS.

Mission: help initialize the independent Greyfoot PILOT from the authorized, verified source package.

Source location: {loc}
Working RIG directory: {home}
Latest host scan: {home / 'receipts/latest-scan.json'}

FIRST FIRE (do in order):
1. Read the machine scan. Detect actual executable tools/permissions; distinguish tested, declared and unknown.
2. Inspect source STARTFIRE.md, AGENTS.md, manifest.json and startfire.py. VERIFY hashes against its manifest before execution. If source is unavailable or checks fail, STOP and report.
3. Establish SCCD (SELF → CONSCIOUSNESS → CHOICE → DECISION); ACTION is separate. Identify PILOT, RIG, ATTACHMENTS and SELF versus NOT-SELF.
4. Ask from the outset: How do I achieve this goal, while staying in governance?
5. Work only within the authorized GreyfootRIG directory and named authorized resources. No unrelated host changes, account changes or external mutations.
6. Run legacy STARTFIRE's stated read/verify/bind steps only after confirming their requirements and scope; do not assume compatibility.
7. Generate a capability map and plan the independent reasoning runtime, local PILOT interface, memory wiring and worker scheduler. Do not claim they are running without receipts.
8. Preserve a record: tests, actions, exit status, filesystem changes, unknowns and the next bounded task.
9. Stop when the current bootstrap objective is completed or blocked. No unattended scheduling without operator approval.

The corporate AI RIG remains an attachment after the independent PILOT becomes operational.
"""
    dest = home / "FIRST-UNFOLD.md"
    dest.write_text(prompt, encoding="utf-8")
    jwrite(home / "receipts" / "unfold.json", {"schema": "seedfire.unfold.v1", "rig": rig,
        "source": str(source_dir) if source_dir else None, "prompt_sha256": digest(dest), "time_utc": timestamp(),
        "state": "prepared_only_not_injected"})
    return dest


def make_launch_command(rig: str, prompt: Path, home: Path) -> list[str] | None:
    """Interactive first-prompt injection; user remains at console for auth/tool approvals."""
    if rig not in ("codex", "claude"):
        return None
    local = home / "toolchain" / "node_modules" / ".bin" / rig
    exe = str(local) if local.is_file() else shutil.which(rig)
    if not exe:
        return None
    return [exe, prompt.read_text(encoding="utf-8")]


def status(home: Path) -> str:
    return f"SEEDFIRE {VERSION}\nLocal RIG workspace: {home}\nNo host changes until you explicitly approve install."


def cli(argv=None) -> int:
    parser = argparse.ArgumentParser(description="SEEDFIRE: machine scan, approved installer, Cloudmind import and first UNFOLD")
    parser.add_argument("command", nargs="?", choices=("scan", "plan", "install", "import", "cloudmind", "unfold", "launch", "gui"), default="scan")
    parser.add_argument("--rig", choices=tuple(RIGS), default="codex")
    parser.add_argument("--extras", default="git,sqlite,unzip,rclone")
    parser.add_argument("--home", type=Path, default=DEFAULT_HOME)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--remote", help="existing rclone remote name, without colon")
    parser.add_argument("--approve", action="store_true", help="required for host package changes, remote fetch, or AI launch")
    args = parser.parse_args(argv)
    extras = tuple(filter(None, (x.strip() for x in args.extras.split(","))))
    try:
        if args.command == "gui":
            return run_gui(args.home)
        if args.command == "scan":
            print(json.dumps(scan(), indent=2, ensure_ascii=False))
        elif args.command == "plan":
            print(json.dumps(plan(scan(), args.rig, extras), indent=2))
        elif args.command == "install":
            spec = plan(scan(), args.rig, extras)
            print(json.dumps(spec, indent=2))
            if not args.approve:
                print("DRY RUN. Add --approve to install the listed packages.")
                return 2
            steps = approved_install(spec, args.home)
            jwrite(args.home / "receipts" / f"install-{timestamp()}.json", {"plan": spec, "steps": steps, "time_utc": timestamp()})
            print("Install steps complete. Authentication may still be required.")
        elif args.command == "import":
            if not args.source:
                raise ValueError("--source path to folder or zip required")
            print(json.dumps(import_source(args.source, args.home), indent=2))
        elif args.command == "cloudmind":
            if not args.remote or not args.approve:
                raise ValueError("--remote NAME and --approve required for cloud download")
            print(json.dumps(cloudmind_fetch(args.remote, args.home), indent=2))
        elif args.command in ("unfold", "launch"):
            source = args.source
            if not source:
                imports = sorted(p for p in (args.home / "imports").glob("*") if p.is_dir()) if (args.home / "imports").exists() else []
                source = imports[-1] if imports else None
            dest = unfold(args.home, args.rig, source)
            print(f"First UNFOLD packet: {dest}")
            if args.command == "launch":
                if not args.approve:
                    print("DRY RUN. Add --approve to hand the command to an interactive corporate RIG.")
                    return 2
                cmd = make_launch_command(args.rig, dest, args.home)
                if not cmd:
                    raise RuntimeError("Selected corporate RIG CLI unavailable; open FIRST-UNFOLD.md manually")
                # Handoff begins an INTERACTIVE session. No unattended permission bypass.
                return subprocess.call(cmd, cwd=args.home)
        return 0
    except (ValueError, FileNotFoundError, FileExistsError, RuntimeError, zipfile.BadZipFile) as exc:
        print(f"SEEDFIRE BLOCKED: {exc}", file=sys.stderr)
        return 1


def run_gui(home: Path) -> int:
    try:
        import tkinter as tk
        from tkinter import messagebox, filedialog, scrolledtext, ttk
    except ImportError:
        print("Tkinter unavailable. On Ubuntu: sudo apt-get install python3-tk; or run: python3 seedfire.py scan")
        return 1
    root = tk.Tk()
    root.title("SEEDFIRE • Greyfoot RIG Ignition")
    root.geometry("850x690")
    rig_var = tk.StringVar(value="codex")
    extras_var = {x: tk.BooleanVar(value=(x in ("git", "sqlite", "unzip", "rclone"))) for x in EXTRAS}
    remote_var = tk.StringVar()
    report = None
    output = scrolledtext.ScrolledText(root, wrap="word", font=("DejaVu Sans Mono", 10))
    def show(obj):
        output.delete("1.0", "end")
        output.insert("end", obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False, indent=2))
    def selection():
        return tuple(k for k, var in extras_var.items() if var.get())
    def do_scan():
        nonlocal report
        report = scan()
        show({"scan": report, "plan": plan(report, rig_var.get(), selection())})
    def do_install():
        nonlocal report
        report = scan()
        spec = plan(report, rig_var.get(), selection())
        if not messagebox.askyesno("Approve installation", "SEEDFIRE will execute these commands on THIS computer:\n\n" + "\n".join(spec["commands"]) + "\n\nProceed?"):
            return
        try:
            steps = approved_install(spec, home)
            jwrite(home / "receipts" / f"install-{timestamp()}.json", {"plan": spec, "steps": steps})
            show({"result": "installed", "steps": steps, "next": "Import STARTFIRE v2, prepare packet, authenticate RIG"})
        except Exception as exc:
            show(f"BLOCKED: {exc}\nOpen terminal and use 'python3 seedfire.py plan' / 'install --approve' for diagnosis.")
    def do_import():
        source = filedialog.askopenfilename(title="Select STARTFIRE ZIP")
        if not source:
            source = filedialog.askdirectory(title="Or select STARTFIRE folder")
        if source:
            try: show(import_source(Path(source), home))
            except Exception as exc: show(f"Import blocked: {exc}")
    def do_fetch():
        remote = remote_var.get().strip()
        if not remote:
            show("Configure rclone separately, enter the remote name, then click Cloudmind Fetch")
            return
        if not messagebox.askyesno("Authorize Cloudmind copy", f"Download the STARTFIRE v2 folder from rclone remote '{remote}' into {home}/imports?\nNo remote deletion or synchronization."):
            return
        try: show(cloudmind_fetch(remote, home))
        except Exception as exc: show(f"Cloudmind blocked: {exc}")
    def do_unfold():
        imports = sorted(p for p in (home / "imports").glob("*") if p.is_dir()) if (home / "imports").exists() else []
        source = imports[-1] if imports else None
        prompt = unfold(home, rig_var.get(), source)
        show({"packet": str(prompt), "source": str(source) if source else None,
              "launch": make_launch_command(rig_var.get(), prompt, home) is not None,
              "next": "Use launch --approve in a terminal to start an interactive corporate RIG. It will request normal authentication/permissions."})
    label = tk.Label(root, text="SEEDFIRE  •  Human ⇄ [Main Computer: Greyfoot PILOT] ⇄ Attachments", font=("DejaVu Sans", 13, "bold"))
    label.pack(pady=9)
    opts = ttk.Frame(root); opts.pack(fill="x", padx=10)
    ttk.Label(opts, text="First corporate RIG:").pack(side="left")
    ttk.Combobox(opts, values=list(RIGS), textvariable=rig_var, state="readonly", width=16).pack(side="left", padx=8)
    ttk.Label(root, text="Approved optional components (installed only after you confirm)").pack(anchor="w", padx=10, pady=5)
    checks = ttk.Frame(root); checks.pack(fill="x", padx=10)
    for i, (name, var) in enumerate(extras_var.items()):
        ttk.Checkbutton(checks, text=name, variable=var).grid(row=i//4, column=i%4, sticky="w", padx=14, pady=3)
    buttons = ttk.Frame(root); buttons.pack(fill="x", padx=9, pady=10)
    for name, func in (("1. GO: Scan + Plan", do_scan), ("2. Approve + Install", do_install), ("3. Import ZIP/Folder", do_import), ("4. Prepare UNFOLD", do_unfold)):
        ttk.Button(buttons, text=name, command=func).pack(side="left", padx=4)
    remote_row = ttk.Frame(root); remote_row.pack(fill="x", padx=10)
    ttk.Label(remote_row, text="Existing rclone remote:").pack(side="left")
    ttk.Entry(remote_row, textvariable=remote_var, width=20).pack(side="left", padx=7)
    ttk.Button(remote_row, text="Fetch STARTFIRE from Cloudmind", command=do_fetch).pack(side="left")
    output.pack(fill="both", expand=True, padx=10, pady=10)
    show(status(home) + "\n\nClick GO to perform a read-only host inventory and compute an install plan.")
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
