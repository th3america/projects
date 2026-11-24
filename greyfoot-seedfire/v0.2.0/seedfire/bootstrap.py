#!/usr/bin/env python3
"""SEEDFIRE v0.2.0 — local-first Greyfoot bootstrap scaffold. Read-only by default."""
from __future__ import annotations
import argparse, hashlib, json, os, platform, shutil, subprocess, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = Path.home() / ".local" / "share" / "greyfoot-seedfire"
DEFAULT_MODEL = "qwen3:8b"

def command_version(cmd, args):
    exe = shutil.which(cmd)
    if not exe: return None
    try:
        p = subprocess.run([exe, *args], text=True, capture_output=True, timeout=8)
        return (p.stdout or p.stderr).strip().splitlines()[0][:200]
    except Exception as e: return f"detected; version probe failed: {e}"

def gpu_probe():
    exe = shutil.which("nvidia-smi")
    if not exe: return {"available": False, "reason": "nvidia-smi not found; CPU inference remains available"}
    try:
        p = subprocess.run([exe, "--query-gpu=name,memory.total", "--format=csv,noheader"], capture_output=True, text=True, timeout=8)
        return {"available": p.returncode == 0, "detail": p.stdout.strip() or p.stderr.strip()}
    except Exception as e: return {"available": False, "reason": str(e)}

def scan():
    mem_kb = None
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemTotal:"): mem_kb = int(line.split()[1]); break
    except OSError: pass
    disk = shutil.disk_usage(Path.home())
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(), "system": platform.system(),
        "machine": platform.machine(), "python": platform.python_version(),
        "cpu_logical_count": os.cpu_count(),
        "memory_total_gib": round(mem_kb / 1024 / 1024, 2) if mem_kb else None,
        "home_disk_total_gib": round(disk.total / 1024**3, 2),
        "home_disk_free_gib": round(disk.free / 1024**3, 2),
        "tools": {k: command_version(k, a) for k,a in {
            "git":["--version"], "docker":["--version"], "ollama":["--version"],
            "curl":["--version"], "ssh":["-V"], "systemctl":["--version"]}.items()},
        "gpu": gpu_probe()
    }

def plan(report, model):
    return {
        "mode":"local_first",
        "host":{k:report.get(k) for k in ("system","machine","cpu_logical_count","memory_total_gib","home_disk_free_gib")},
        "model":model,
        "steps":[
            {"id":"install_ollama","description":"Download and review official Ollama Linux installer, then execute only after approval","requires_root":True},
            {"id":"enable_ollama","description":"Enable and start Ollama service after approval","requires_root":True},
            {"id":"pull_model","description":f"Download {model}; model disk/RAM use depends on quantization","requires_root":False},
            {"id":"verify_model","description":"Run local inference smoke test","requires_root":False},
            {"id":"startfire_restore","description":"Verify private STARTFIRE 003 payload and initialize portable Mindvault when supplied","requires_root":False}
        ],
        "not_in_scope_yet":["automatic SSH exposure changes","corporate UI login or credential handling","GPU marketplace purchases","unattended Cloudmind synchronization"]
    }

def confirm(prompt):
    return input(prompt + " [type YES to continue]: ").strip() == "YES"

def run(cmd, timeout=None):
    print("$", " ".join(cmd))
    subprocess.run(cmd, check=True, timeout=timeout)

def install_ollama():
    if not shutil.which("ollama"):
        installer = STATE / "ollama-install.sh"
        STATE.mkdir(parents=True, exist_ok=True)
        print("Downloading official Ollama installer to", installer)
        urllib.request.urlretrieve("https://ollama.com/install.sh", installer)
        print("Installer SHA-256:", hashlib.sha256(installer.read_bytes()).hexdigest())
        print("Review this script before approval:", installer)
        if not confirm("Execute downloaded installer with sudo?"):
            raise SystemExit("Cancelled; installer not executed.")
        run(["sudo","bash",str(installer)], timeout=900)
    else: print("Ollama already installed.")
    if shutil.which("systemctl") and confirm("Enable and start Ollama with systemd?"):
        run(["sudo","systemctl","enable","--now","ollama"])

def pull_model(model):
    if not shutil.which("ollama"): raise SystemExit("Ollama not installed.")
    if not confirm(f"Download {model}? This uses disk and bandwidth."): raise SystemExit("Cancelled.")
    run(["ollama","pull",model], timeout=7200)
    run(["ollama","run",model,"Reply with exactly: SEEDFIRE_LOCAL_MODEL_OK"], timeout=600)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    sub=ap.add_subparsers(dest="action",required=True)
    sub.add_parser("scan")
    pp=sub.add_parser("plan"); pp.add_argument("--model",default=DEFAULT_MODEL)
    aa=sub.add_parser("apply"); aa.add_argument("--model",default=DEFAULT_MODEL); aa.add_argument("--skip-model",action="store_true")
    args=ap.parse_args()
    if args.action=="scan":
        report=scan(); STATE.mkdir(parents=True,exist_ok=True)
        (STATE/"host-scan.json").write_text(json.dumps(report,indent=2)); print(json.dumps(report,indent=2))
    elif args.action=="plan":
        report=scan(); result=plan(report,args.model); STATE.mkdir(parents=True,exist_ok=True)
        (STATE/"install-plan.json").write_text(json.dumps(result,indent=2)); print(json.dumps(result,indent=2))
    else:
        result=plan(scan(),args.model); print(json.dumps(result,indent=2))
        if not confirm("Approve local Ollama bootstrap?"): raise SystemExit("No changes made.")
        install_ollama()
        if not args.skip_model: pull_model(args.model)
        print("Local inference bootstrap completed. Full Greyfoot PILOT is not yet initialized.")

if __name__=="__main__": main()
