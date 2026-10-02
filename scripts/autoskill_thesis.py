#!/usr/bin/env python3
"""
autoskill_thesis.py — Automated Research Skill & Workflow Synthesizer for Master's Thesis.

Purpose:
  Provides a local, zero-external-dependency skill manager and synthesizer tailored
  to the MSc Thesis research workflow. Enables:
    1. doctor: Verify all solver environments (WSL Ubuntu, Fast Downward, FastLAS, Clingo, Python).
    2. scan: Detect recent workflow patterns from git log, research-log.md, and benchmark_outputs.
    3. draft: Auto-synthesize or scaffold a new Antigravity SKILL.md based on a domain or task.
    4. validate: Verify all existing skills against RESEARCH_RULES.md and Antigravity schema.
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"


def check_command(cmd, shell=False):
    try:
        res = subprocess.run(
            cmd,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
        )
        return res.returncode == 0, res.stdout.strip()
    except Exception as e:
        return False, str(e)


def run_doctor():
    print("=" * 60)
    print("  [AutoSkill Thesis] Environment Preflight & Diagnostic")
    print("=" * 60)
    
    # 1. Python environment
    print(f"[*] Host Python: {sys.version.split()[0]} ({sys.executable})")
    
    # 2. PDDL library
    try:
        import pddl
        print(f"  [+] Python 'pddl' package: OK ({pddl.__file__})")
    except ImportError:
        print("  [-] Python 'pddl' package: NOT FOUND (Run: pip install pddl)")

    # 3. WSL Ubuntu
    wsl_ok, wsl_out = check_command(["wsl", "-d", "Ubuntu", "-e", "echo", "WSL_OK"])
    if wsl_ok and "WSL_OK" in wsl_out:
        print("  [+] WSL Ubuntu Container: REACHABLE")
    else:
        print("  [-] WSL Ubuntu Container: UNREACHABLE or NOT INSTALLED")

    # 4. Fast Downward inside WSL
    fd_ok, fd_out = check_command(["wsl", "-d", "Ubuntu", "-e", "bash", "-c", "which fast-downward || which downward || ls /mnt/f/Thesis/bin/downward 2>/dev/null"])
    if fd_ok and fd_out:
        print(f"  [+] Fast Downward: FOUND ({fd_out})")
    else:
        print("  [!] Fast Downward: Custom path in /mnt/f/Thesis/bin or venv_linux")

    # 5. Clingo / FastLAS
    clingo_ok, _ = check_command(["wsl", "-d", "Ubuntu", "-e", "which", "clingo"])
    print(f"  [{'+' if clingo_ok else '!'}] Clingo (ASP solver in WSL): {'INSTALLED' if clingo_ok else 'Check venv_linux'}")

    # 6. Repository Skills Check
    existing_skills = [d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]
    print(f"  [+] Active Workspace Skills ({len(existing_skills)}): {', '.join(existing_skills)}")

    print("\nPreflight check completed.")


def run_scan():
    print("=" * 60)
    print("  [AutoSkill Thesis] Scanning Research Traces & Workflow History")
    print("=" * 60)

    # Scan research-log.md
    log_file = REPO_ROOT / "research-log.md"
    if log_file.exists():
        content = log_file.read_text(encoding="utf-8")
        entries = re.findall(r"##\s*(\d{4}-\d{2}-\d{2}[^–\n]*)", content)
        print(f"[*] Research Log Entries Found: {len(entries)}")
        if entries:
            print(f"    Latest: {entries[-1].strip()}")
    else:
        print("[-] research-log.md not found.")

    # Scan benchmark_outputs
    out_dir = REPO_ROOT / "benchmark_outputs"
    if out_dir.exists():
        files = list(out_dir.glob("*.*"))
        print(f"[*] Benchmark Artifacts: {len(files)} files recorded.")
    else:
        print("[!] benchmark_outputs directory does not exist yet.")

    # Check git recent commits
    git_ok, git_out = check_command(["git", "log", "-n", "3", "--oneline"], shell=False)
    if git_ok:
        print("\n[*] Recent Git Commits:")
        for line in git_out.splitlines():
            print(f"    {line}")

    print("\nScan completed. Use 'draft' to scaffold missing workflow skills.")


def run_validate():
    print("=" * 60)
    print("  [AutoSkill Thesis] Validating Workspace Skills")
    print("=" * 60)

    all_valid = True
    for skill_path in SKILLS_DIR.glob("*/SKILL.md"):
        skill_name = skill_path.parent.name
        content = skill_path.read_text(encoding="utf-8")
        
        # Check YAML frontmatter
        if not content.startswith("---"):
            print(f"[-] {skill_name}: Missing YAML frontmatter marker '---'")
            all_valid = False
            continue
        
        frontmatter_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not frontmatter_match:
            print(f"[-] {skill_name}: Malformed YAML frontmatter")
            all_valid = False
            continue
            
        frontmatter = frontmatter_match.group(1)
        if "name:" not in frontmatter or "description:" not in frontmatter:
            print(f"[-] {skill_name}: Missing required 'name' or 'description' in frontmatter")
            all_valid = False
            continue

        # Check compliance with RESEARCH_RULES.md
        if "RESEARCH_RULES" in content or "Zero Synthetic" in content or "Zero fake data" in content:
            print(f"[+] {skill_name}: VALID (Strict RESEARCH_RULES compliance embedded)")
        else:
            print(f"[!] {skill_name}: WARNING - No explicit mention of RESEARCH_RULES.md")

    if all_valid:
        print("\nAll workspace skills passed schema validation.")
    else:
        print("\nSome skills had validation issues.")


def run_draft(name, description):
    target_dir = SKILLS_DIR / name
    target_file = target_dir / "SKILL.md"
    
    if target_file.exists():
        print(f"[-] Skill '{name}' already exists at {target_file}")
        return

    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "scripts").mkdir(exist_ok=True)
    (target_dir / "references").mkdir(exist_ok=True)

    template = f"""---
name: {name}
description: {description}
metadata:
  model: inherit
---

# {name.replace('-', ' ').title()} Skill

## 1. Purpose & Scope
{description}

## 2. Mandatory Rules (`RESEARCH_RULES.md`)
- Zero synthetic/random mock data (`np.random` banned).
- All empirical numbers must stem from real native solver runs.

## 3. Workflow Procedures
1. Input verification.
2. Solver execution in WSL Ubuntu (`venv_linux`).
3. Output parsing and validation against PDDL standards.
4. Non-parametric statistical evaluation.

## 4. References & Documentation
- Consult `references/` for mathematical specifications.
"""
    target_file.write_text(template, encoding="utf-8")
    print(f"[+] Successfully drafted new skill: {target_file}")


def main():
    parser = argparse.ArgumentParser(description="AutoSkill Thesis: Skill Manager & Workflow Synthesizer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("doctor", help="Run environment preflight & diagnostic")
    subparsers.add_parser("scan", help="Scan workflow history and research logs")
    subparsers.add_parser("validate", help="Validate all workspace skills")

    draft_parser = subparsers.add_parser("draft", help="Draft a new Antigravity skill")
    draft_parser.add_argument("--name", required=True, help="Skill directory/identifier (kebab-case)")
    draft_parser.add_argument("--desc", required=True, help="Description for skill triggering")

    args = parser.parse_args()

    if args.command == "doctor":
        run_doctor()
    elif args.command == "scan":
        run_scan()
    elif args.command == "validate":
        run_validate()
    elif args.command == "draft":
        run_draft(args.name, args.desc)


if __name__ == "__main__":
    main()
