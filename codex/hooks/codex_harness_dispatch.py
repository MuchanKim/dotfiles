#!/usr/bin/env python3
import datetime
import json
import os
import pathlib
import re
import subprocess
import sys

CODE_SUFFIXES = (
    ".swift",
    ".kt",
    ".java",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".py",
    ".go",
    ".rs",
    ".c",
    ".cpp",
    ".h",
    ".m",
    ".mm",
    ".plist",
    ".json",
    ".yaml",
    ".yml",
    ".pbxproj",
    ".xcodeproj",
)

HOOKS_DIR = pathlib.Path(__file__).resolve().parent
DISPATCH_LOG_PATH = HOOKS_DIR / "codex_harness_dispatch.log"
STOP_LOG_PATH = HOOKS_DIR / "harness_stop_check.log"
LOG_CLEANUP_PATHS = (
    DISPATCH_LOG_PATH,
    STOP_LOG_PATH,
    HOOKS_DIR / "codex_harness_plugin_probe.log",
    HOOKS_DIR / "user_prompt_submit_probe.log",
)


def load_payload():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return {}
        payload = json.loads(raw)
        return payload if isinstance(payload, dict) else {}
    except json.JSONDecodeError:
        return {}


def event_name_from(payload):
    event_name = payload.get("hook_event_name")
    if isinstance(event_name, str) and event_name:
        return event_name
    if len(sys.argv) > 1 and sys.argv[1]:
        return sys.argv[1]
    return "Unknown"


def cwd_from(payload):
    cwd = payload.get("cwd")
    return cwd if isinstance(cwd, str) and cwd else os.getcwd()


def append_jsonl(path, record):
    try:
        with pathlib.Path(path).open("a", encoding="utf-8") as log_file:
            log_file.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    except OSError:
        pass


def log_dispatch(event_name, cwd, decision, reason):
    append_jsonl(
        DISPATCH_LOG_PATH,
        {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "event_name": event_name,
            "cwd": str(cwd),
            "decision": decision,
            "reason": reason,
        },
    )


def cleanup_runtime_logs():
    for path in LOG_CLEANUP_PATHS:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        except OSError:
            pass


def append_stop_log(event_name, cwd, repo_root_present, changed_file_count, decision, reason):
    append_jsonl(
        STOP_LOG_PATH,
        {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "event_name": event_name,
            "cwd": str(cwd),
            "repo_root_present": bool(repo_root_present),
            "changed_file_count": int(changed_file_count),
            "decision": decision,
            "reason": reason,
        },
    )


def emit_context(message):
    # Keep Stop non-blocking. Codex may surface additionalContext as model feedback;
    # unsupported keys are ignored by older runtimes.
    print(json.dumps({"additionalContext": message, "message": message}))


def emit_quiet():
    print("{}")


def run_git(args, cwd):
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout


def changed_paths(repo_root):
    paths = []
    for args in (["diff", "--name-only"], ["diff", "--cached", "--name-only"]):
        output = run_git(args, repo_root)
        if output is None:
            continue
        paths.extend(line.strip() for line in output.splitlines() if line.strip())
    return sorted(set(paths))


def has_code_like_change(paths):
    return any(path.endswith(CODE_SUFFIXES) for path in paths)


def parse_section_status(path, section_name, allowed):
    allowed_map = {value.lower(): value.lower() for value in allowed}
    try:
        lines = pathlib.Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None

    in_section = False
    for raw_line in lines:
        line = raw_line.strip()
        if line.lower() == f"## {section_name}".lower():
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section:
            continue
        if "/" in line:
            continue
        normalized = line.strip("-*` ").lower()
        if normalized in allowed_map:
            return allowed_map[normalized]
        for value in allowed_map:
            if re.fullmatch(rf"[-*` ]*{re.escape(value)}[` ]*", line, flags=re.IGNORECASE):
                return value
    return None


def handle_user_prompt_submit(_event_name, _cwd):
    emit_quiet()
    return 0


def handle_subagent_lifecycle(event_name, cwd):
    repo_root_output = run_git(["rev-parse", "--show-toplevel"], cwd)
    if repo_root_output:
        current_task_path = pathlib.Path(repo_root_output.strip()) / ".codex" / "current-task"
        if current_task_path.exists():
            reason = "subagent_started" if event_name == "SubagentStart" else "subagent_stopped"
            log_dispatch(event_name, cwd, "silent", reason)
    emit_quiet()
    return 0


def handle_stop(event_name, cwd):
    repo_root_output = run_git(["rev-parse", "--show-toplevel"], cwd)
    if not repo_root_output:
        emit_quiet()
        return 0

    repo_root = pathlib.Path(repo_root_output.strip())
    paths = changed_paths(str(repo_root))
    if not paths:
        emit_quiet()
        return 0

    if not has_code_like_change(paths):
        emit_quiet()
        return 0

    project_codex = repo_root / ".codex"
    current_task_path = project_codex / "current-task"
    if not current_task_path.exists():
        log_dispatch(event_name, cwd, "warning", "missing_current_task")
        append_stop_log(event_name, cwd, True, len(paths), "warning", "missing_current_task")
        emit_context(
            "Codex harness warning: code changes detected, but .codex/current-task is missing."
        )
        return 0

    try:
        task_id = current_task_path.read_text(encoding="utf-8", errors="replace").strip().splitlines()[0].strip()
    except (OSError, IndexError):
        task_id = ""

    if not task_id:
        log_dispatch(event_name, cwd, "warning", "empty_current_task")
        append_stop_log(event_name, cwd, True, len(paths), "warning", "empty_current_task")
        emit_context("Codex harness warning: .codex/current-task is empty.")
        return 0

    run_dir = project_codex / "runs" / task_id
    reports = {
        "planning": run_dir / "01-planning.md",
        "implementation": run_dir / "02-implementation-report.md",
        "verification": run_dir / "03-verification-report.md",
        "review-correctness": run_dir / "04-review-correctness.md",
        "review-verification-risk": run_dir / "04-review-verification-risk.md",
        "final-decision": run_dir / "05-final-decision.md",
    }

    missing = [name for name, path in reports.items() if not path.exists()]
    if missing:
        log_dispatch(event_name, cwd, "warning", "missing_reports")
        append_stop_log(event_name, cwd, True, len(paths), "warning", "missing_reports")
        emit_context(
            "Codex harness warning: missing reports for task "
            f"{task_id}: {', '.join(missing)}."
        )
        return 0

    verification = parse_section_status(
        reports["verification"],
        "Verdict",
        ("pass", "fail", "inconclusive"),
    )
    review_correctness = parse_section_status(
        reports["review-correctness"],
        "Verdict",
        ("pass", "pass_with_notes", "major", "blocker"),
    )
    review_verification_risk = parse_section_status(
        reports["review-verification-risk"],
        "Verdict",
        ("pass", "pass_with_notes", "major", "blocker"),
    )
    readiness = parse_section_status(
        reports["final-decision"],
        "Commit Readiness",
        ("ready", "not_ready"),
    )

    warnings = []
    if verification != "pass":
        warnings.append(f"verification={verification or 'unknown'}")
    if review_correctness not in ("pass", "pass_with_notes"):
        warnings.append(f"review_correctness={review_correctness or 'unknown'}")
    if review_verification_risk not in ("pass", "pass_with_notes"):
        warnings.append(f"review_verification_risk={review_verification_risk or 'unknown'}")
    if readiness != "ready":
        warnings.append(f"readiness={readiness or 'unknown'}")

    if warnings:
        log_dispatch(event_name, cwd, "warning", "reports_not_ready")
        append_stop_log(event_name, cwd, True, len(paths), "warning", "reports_not_ready")
        emit_context(
            "Codex harness warning: task "
            f"{task_id} is not ready ({'; '.join(warnings)})."
        )
        return 0

    log_dispatch(event_name, cwd, "ready", "reports_ready")
    append_stop_log(event_name, cwd, True, len(paths), "ready", "reports_ready")
    cleanup_runtime_logs()
    emit_context(f"Codex harness ready: task {task_id} has passed verification and both reviews.")
    return 0


def main():
    payload = load_payload()
    event_name = event_name_from(payload)
    cwd = cwd_from(payload)

    if event_name == "UserPromptSubmit":
        return handle_user_prompt_submit(event_name, cwd)
    if event_name in ("SubagentStart", "SubagentStop"):
        return handle_subagent_lifecycle(event_name, cwd)
    if event_name == "Stop":
        return handle_stop(event_name, cwd)

    log_dispatch(event_name, cwd, "silent", "unsupported_event")
    emit_quiet()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
