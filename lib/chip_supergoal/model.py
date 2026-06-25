from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any

_ALLOWED_TOP_LEVEL = {
    "schema_version", "protocol_version", "contract_revision", "profile", "goal",
    "source_set", "decisions", "architecture", "loop", "risks", "approvals",
    "phases", "delivery", "compatibility",
}

@dataclass(frozen=True)
class Goal:
    id: str
    title: str
    objective: str
    request_digest: str
    workspace_root: str
    owner: str
    non_goals: list[str]
    done_condition: str
    created_at: str | None = None

@dataclass(frozen=True)
class Source:
    id: str
    kind: str
    locator: str
    authority: str
    freshness: str
    sensitivity: str = "internal"
    sha256: str | None = None
    used_by: list[str] = field(default_factory=list)

@dataclass(frozen=True)
class Architecture:
    data: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class Loop:
    data: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class Risk:
    id: str
    tag: str
    severity: str = "P2"
    mitigation: str = ""

@dataclass(frozen=True)
class Approval:
    id: str
    class_name: str
    scope: str
    required: bool = True

@dataclass(frozen=True)
class Verifier:
    type: str
    command_id: str | None = None
    expected_exit: int | None = None
    expected_assertion: str | None = None

@dataclass(frozen=True)
class Criterion:
    id: str
    statement: str
    verifier: Verifier
    evidence_tier: str
    blocking: bool = True

@dataclass(frozen=True)
class Command:
    id: str
    command: str
    purpose: str
    safety: str = "local_read_write"
    timeout_seconds: int = 120

@dataclass(frozen=True)
class Deliverable:
    id: str
    kind: str
    path: str
    change_expectation: str
    verification: str

@dataclass(frozen=True)
class RpdPolicy:
    required: bool
    focus: list[str]

@dataclass(frozen=True)
class Phase:
    id: str
    ordinal: int
    name: str
    task: str
    depends_on: list[str]
    work_items: list[dict[str, Any]]
    deliverables: list[Deliverable]
    criteria: list[Criterion]
    commands: list[Command]
    risk_tags: list[str]
    rpd: RpdPolicy

@dataclass(frozen=True)
class Delivery:
    data: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class Contract:
    schema_version: str
    protocol_version: str
    contract_revision: int
    profile: str
    goal: Goal
    source_set: list[Source]
    decisions: list[dict[str, Any]]
    architecture: Architecture
    loop: Loop
    risks: list[Risk]
    approvals: list[Approval]
    phases: list[Phase]
    delivery: Delivery
    compatibility: dict[str, Any]


def _unknown_keys(data: dict[str, Any], allowed: set[str], label: str) -> None:
    extra = sorted(set(data) - allowed)
    if extra:
        raise ValueError(f"unknown {label} field(s): {', '.join(extra)}")

def _goal(data: dict[str, Any]) -> Goal:
    allowed = {"id","title","objective","request_digest","workspace_root","owner","non_goals","done_condition","created_at"}
    _unknown_keys(data, allowed, "goal")
    return Goal(**{k: data.get(k) for k in allowed if k in data})

def _source(data: dict[str, Any]) -> Source:
    allowed = {"id","kind","locator","authority","freshness","sensitivity","sha256","used_by"}
    _unknown_keys(data, allowed, "source")
    return Source(**{k: data.get(k) for k in allowed if k in data})

def _risk(data: dict[str, Any]) -> Risk:
    allowed = {"id","tag","severity","mitigation"}
    _unknown_keys(data, allowed, "risk")
    return Risk(**{k: data.get(k) for k in allowed if k in data})

def _approval(data: dict[str, Any]) -> Approval:
    allowed = {"id","class_name","scope","required"}
    _unknown_keys(data, allowed, "approval")
    return Approval(**{k: data.get(k) for k in allowed if k in data})

def _criterion(data: dict[str, Any]) -> Criterion:
    allowed = {"id","statement","verifier","evidence_tier","blocking"}
    _unknown_keys(data, allowed, "criterion")
    verifier_data = dict(data["verifier"])
    _unknown_keys(verifier_data, {"type","command_id","expected_exit","expected_assertion"}, "verifier")
    return Criterion(id=data["id"], statement=data["statement"], verifier=Verifier(**verifier_data), evidence_tier=data["evidence_tier"], blocking=data.get("blocking", True))

def _command(data: dict[str, Any]) -> Command:
    allowed = {"id","command","purpose","safety","timeout_seconds"}
    _unknown_keys(data, allowed, "command")
    return Command(**{k: data.get(k) for k in allowed if k in data})

def _deliverable(data: dict[str, Any]) -> Deliverable:
    allowed = {"id","kind","path","change_expectation","verification"}
    _unknown_keys(data, allowed, "deliverable")
    return Deliverable(**{k: data.get(k) for k in allowed if k in data})

def _phase(data: dict[str, Any]) -> Phase:
    allowed = {"id","ordinal","name","task","depends_on","work_items","deliverables","criteria","commands","risk_tags","rpd"}
    _unknown_keys(data, allowed, "phase")
    rpd = data.get("rpd", {})
    _unknown_keys(rpd, {"required","focus"}, "rpd")
    return Phase(
        id=data["id"], ordinal=data["ordinal"], name=data["name"], task=data["task"],
        depends_on=list(data.get("depends_on", [])), work_items=list(data.get("work_items", [])),
        deliverables=[_deliverable(x) for x in data.get("deliverables", [])],
        criteria=[_criterion(x) for x in data.get("criteria", [])],
        commands=[_command(x) for x in data.get("commands", [])],
        risk_tags=list(data.get("risk_tags", [])), rpd=RpdPolicy(required=bool(rpd.get("required", False)), focus=list(rpd.get("focus", []))),
    )

def contract_from_dict(data: dict[str, Any], *, strict: bool = True) -> Contract:
    if strict:
        _unknown_keys(data, _ALLOWED_TOP_LEVEL, "contract")
    if data.get("schema_version") != "3.0" or data.get("protocol_version") != "3.0":
        raise ValueError("only contract/protocol version 3.0 is supported")
    return Contract(
        schema_version=data["schema_version"], protocol_version=data["protocol_version"],
        contract_revision=int(data["contract_revision"]), profile=data["profile"],
        goal=_goal(dict(data["goal"])), source_set=[_source(dict(x)) for x in data.get("source_set", [])],
        decisions=list(data.get("decisions", [])), architecture=Architecture(dict(data.get("architecture", {}))),
        loop=Loop(dict(data.get("loop", {}))), risks=[_risk(dict(x)) for x in data.get("risks", [])],
        approvals=[_approval(dict(x)) for x in data.get("approvals", [])],
        phases=[_phase(dict(x)) for x in data.get("phases", [])],
        delivery=Delivery(dict(data.get("delivery", {}))), compatibility=dict(data.get("compatibility", {})),
    )

def load_contract(path: str | Path, *, strict: bool = True) -> Contract:
    return contract_from_dict(json.loads(Path(path).read_text(encoding="utf-8")), strict=strict)

def to_plain(obj: Any) -> Any:
    if hasattr(obj, "__dataclass_fields__"):
        return {k: to_plain(getattr(obj, k)) for k in obj.__dataclass_fields__}
    if isinstance(obj, list):
        return [to_plain(x) for x in obj]
    if isinstance(obj, dict):
        return {k: to_plain(v) for k, v in obj.items()}
    return obj

def canonical_json(contract: Contract) -> str:
    return json.dumps(to_plain(contract), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
