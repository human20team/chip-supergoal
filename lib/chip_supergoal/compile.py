from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from .model import Contract, canonical_json, load_contract
from .render import render_launch_goal, render_loop_design, render_phase, render_roadmap, render_state, render_thinking


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.replace("\r\n", "\n"), encoding="utf-8")


def compile_contract(contract: Contract, out: str | Path, *, template_protocol: str | Path | None = None) -> Path:
    out_path = Path(out)
    if out_path.exists():
        shutil.rmtree(out_path)
    out_path.mkdir(parents=True)
    phases_dir = out_path / "phases"
    scripts_dir = out_path / "scripts"
    phases_dir.mkdir(); scripts_dir.mkdir()
    _write(out_path / "CONTRACT.json", canonical_json(contract))
    _write(out_path / "THINKING.md", render_thinking(contract))
    _write(out_path / "LOOP_DESIGN.md", render_loop_design(contract))
    _write(out_path / "ROADMAP.md", render_roadmap(contract))
    _write(out_path / "STATE.md", render_state(contract))
    _write(out_path / "LAUNCH_GOAL.md", render_launch_goal(contract, out_path.as_posix()))
    protocol_text = Path(template_protocol).read_text(encoding="utf-8") if template_protocol else "# PROTOCOL\n\nAUDIT_COMPLETE\nSUPERGOAL_RUN_COMPLETE\n"
    _write(out_path / "PROTOCOL.md", protocol_text)
    for i in range(len(contract.phases)):
        _write(phases_dir / f"phase-{i+1:02d}.md", render_phase(contract, i))
    manifest = build_manifest(out_path)
    _write(out_path / "MANIFEST.json", json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return out_path


def compile_contract_file(path: str | Path, out: str | Path, *, template_protocol: str | Path | None = None) -> Path:
    return compile_contract(load_contract(path), out, template_protocol=template_protocol)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_manifest(root: Path) -> dict:
    artifacts = []
    for p in sorted(x for x in root.rglob("*") if x.is_file() and x.name != "MANIFEST.json"):
        rel = p.relative_to(root).as_posix()
        artifacts.append({"path": rel, "sha256": file_sha256(p), "bytes": p.stat().st_size, "mode": "0644"})
    joined = "\n".join(f"{a['path']} {a['sha256']} {a['bytes']}" for a in artifacts)
    return {"manifest_version": "1.0", "artifacts": artifacts, "package_fingerprint": hashlib.sha256(joined.encode()).hexdigest()}
