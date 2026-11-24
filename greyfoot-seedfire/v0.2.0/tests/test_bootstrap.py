import importlib.util
from pathlib import Path

P=Path(__file__).resolve().parents[1]/"seedfire"/"bootstrap.py"
spec=importlib.util.spec_from_file_location("seedfire_bootstrap",P)
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def test_scan_reports_expected_keys():
    r=mod.scan()
    for k in ("system","machine","cpu_logical_count","home_disk_free_gib","tools","gpu"): assert k in r

def test_plan_is_local_first():
    p=mod.plan({"system":"Linux","machine":"x86_64","cpu_logical_count":12,"memory_total_gib":48,"home_disk_free_gib":300},"qwen3:8b")
    assert p["mode"]=="local_first" and p["model"]=="qwen3:8b"
    assert any(x["id"]=="install_ollama" for x in p["steps"])
    assert "corporate UI login or credential handling" in p["not_in_scope_yet"]
