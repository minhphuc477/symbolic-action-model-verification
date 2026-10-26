"""Mechanical audit: every quantitative claim in the docs must match a summary file.

Claims live in ``docs/research/claims.yaml``::

    - id: rq1_rho
      summary: results/main/summary.json
      path: rq1.spearman_rho
      value: 0.41
      tol: 0.005

``path`` is dot-separated; list elements are selected with ``name[key=val,key=val]``.
Each claim id must be cited in ``docs/research/findings.md`` as ``[claim:<id>]`` and every
cited id must exist in ``claims.yaml``. Exit code is non-zero on any failure.

Usage::

    python -m experiments.claim_audit
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

CLAIMS = Path("docs/research/claims.yaml")
FINDINGS = Path("docs/research/findings.md")
_SEL = re.compile(r"^(\w+)\[(.+)\]$")


def _coerce(raw: str) -> Any:
    for cast in (int, float):
        try:
            return cast(raw)
        except ValueError:
            pass
    return {"true": True, "false": False}.get(raw, raw)


def resolve(obj: Any, path: str) -> Any:
    for part in path.split("."):
        m = _SEL.match(part)
        if m is None:
            obj = obj[int(part)] if isinstance(obj, list) else obj[part]
            continue
        name, cond = m.groups()
        want = {k: _coerce(v) for k, v in (c.split("=", 1) for c in cond.split(","))}
        hits = [e for e in obj[name] if all(e.get(k) == v for k, v in want.items())]
        if len(hits) != 1:
            raise KeyError(f"selector {part!r} matched {len(hits)} entries")
        obj = hits[0]
    return obj


def check(claim: dict[str, Any]) -> str | None:
    """Return an error message, or None if the claim matches."""
    try:
        data = json.loads(Path(claim["summary"]).read_text(encoding="utf-8"))
        actual = resolve(data, claim["path"])
    except (OSError, KeyError, IndexError, ValueError) as exc:
        return f"cannot resolve: {exc}"
    expected = claim["value"]
    if isinstance(expected, (int, float)) and not isinstance(expected, bool):
        if actual is None or abs(float(actual) - float(expected)) > float(claim.get("tol", 0)):
            return f"expected {expected} (tol {claim.get('tol', 0)}), got {actual}"
    elif actual != expected:
        return f"expected {expected!r}, got {actual!r}"
    return None


def main() -> int:
    claims = yaml.safe_load(CLAIMS.read_text(encoding="utf-8")) or []
    ids = {c["id"] for c in claims}
    cited = set(re.findall(r"\[claim:([\w\-]+)\]", FINDINGS.read_text(encoding="utf-8")))
    failures = [f"{c['id']}: {msg}" for c in claims if (msg := check(c))]
    failures += [f"{i}: cited in findings.md but not defined" for i in sorted(cited - ids)]
    failures += [f"{i}: defined but never cited in findings.md" for i in sorted(ids - cited)]
    for f in failures:
        print("FAIL", f)
    print(
        f"{len(claims) - len(failures)}/{len(claims)} claims verified"
        if not failures
        else f"{len(failures)} problem(s)"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
