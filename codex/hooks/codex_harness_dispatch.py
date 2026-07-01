#!/usr/bin/env python3
import datetime
import json
import os
import pathlib
import re
import subprocess
import sys
import tomllib

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
CONTRACT_PATH = HOOKS_DIR.parent / "harness_contract.toml"
DISPATCH_LOG_PATH = HOOKS_DIR / "codex_harness_dispatch.log"
STOP_LOG_PATH = HOOKS_DIR / "harness_stop_check.log"
LOG_CLEANUP_PATHS = (
    DISPATCH_LOG_PATH,
    STOP_LOG_PATH,
    HOOKS_DIR / "codex_harness_plugin_probe.log",
    HOOKS_DIR / "user_prompt_submit_probe.log",
)
SOURCE_EDIT_TOOLS = {"apply_patch", "Edit", "Write"}
BASH_TOOLS = {"Bash", "bash"}


def load_harness_contract():
    with CONTRACT_PATH.open("rb") as contract_file:
        return tomllib.load(contract_file)


def phase_policy_sets(key):
    return {phase: set(policy.get(key, [])) for phase, policy in PHASES.items()}


def phase_report_transitions():
    return {
        phase: (policy["report_transition"]["report"], policy["report_transition"]["next_phase"])
        for phase, policy in PHASES.items()
        if "report_transition" in policy
    }


HARNESS_CONTRACT = load_harness_contract()
PROMPT_PATTERNS = HARNESS_CONTRACT["prompt_patterns"]
PHASES = HARNESS_CONTRACT["phases"]
REPORT_DEFINITIONS = HARNESS_CONTRACT["reports"]
TOOLS_POLICY = HARNESS_CONTRACT["tools"]
USER_TRANSITIONS = HARNESS_CONTRACT["user_transitions"]
REVIEW_IMPROVEMENT_DECISION = HARNESS_CONTRACT["user_decisions"]["review_improvement"]
REVIEW_GATE = HARNESS_CONTRACT["review_gate"]
COMPLETION_POLICY = HARNESS_CONTRACT["completion"]

BASH_ALLOWED_PHASES = set(TOOLS_POLICY["bash_allowed_phases"])
CURRENT_TASK_WRITE_PHASES = set(TOOLS_POLICY["current_task_write_phases"])
HARNESS_REQUEST_PATTERNS = tuple(PROMPT_PATTERNS["harness_request"])
LIGHT_HARNESS_PATTERNS = tuple(PROMPT_PATTERNS["light_harness"])
APPROVAL_PATTERNS = tuple(PROMPT_PATTERNS["approval"])
REWORK_DECISION_PATTERNS = tuple(PROMPT_PATTERNS["review_improvement_rework"])
DECLINE_DECISION_PATTERNS = tuple(PROMPT_PATTERNS["review_improvement_decline"])
USER_APPROVAL_TRANSITIONS = dict(USER_TRANSITIONS["approval"])
USER_CLARIFICATION_TRANSITIONS = dict(USER_TRANSITIONS["clarification"])
PHASE_ALLOWED_HARNESS_REPORTS = phase_policy_sets("allowed_reports")
PHASE_ALLOWED_SUBAGENTS = phase_policy_sets("allowed_subagents")
PHASE_REPORT_TRANSITIONS = phase_report_transitions()
REVIEW_REPORTS_BY_SUBAGENT = dict(HARNESS_CONTRACT["review_reports_by_subagent"])
PLACEHOLDER_LABELS = set(COMPLETION_POLICY["placeholder_sections"]["labels"])


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


def prompt_text_from(payload):
    values = []
    for key in ("prompt", "user_prompt", "userPrompt", "message", "input"):
        value = payload.get(key)
        if isinstance(value, str):
            values.append(value)
    return "\n".join(values)


def is_harness_request(text):
    lowered = text.lower()
    return any(pattern in lowered for pattern in HARNESS_REQUEST_PATTERNS)


def is_light_harness_request(text):
    lowered = text.lower()
    return any(pattern in lowered for pattern in LIGHT_HARNESS_PATTERNS)


def is_approval_prompt(text):
    lowered = text.lower()
    return any(pattern in lowered for pattern in APPROVAL_PATTERNS)


def is_decline_improvement_decision_prompt(text):
    lowered = text.lower()
    return any(pattern in lowered for pattern in DECLINE_DECISION_PATTERNS)


def is_rework_decision_prompt(text):
    lowered = text.lower()
    return any(pattern in lowered for pattern in REWORK_DECISION_PATTERNS)


def is_finalize_decision_prompt(text):
    lowered = text.lower()
    return is_approval_prompt(text) or any(pattern in lowered for pattern in DECLINE_DECISION_PATTERNS)


def improvement_decision_from_prompt(text):
    if is_decline_improvement_decision_prompt(text):
        return REVIEW_IMPROVEMENT_DECISION["decline_value"]
    if is_rework_decision_prompt(text):
        return REVIEW_IMPROVEMENT_DECISION["rework_value"]
    if is_finalize_decision_prompt(text):
        return REVIEW_IMPROVEMENT_DECISION["decline_value"]
    return None


def user_declined_improvement(state):
    return state.get(REVIEW_IMPROVEMENT_DECISION["state_key"]) == REVIEW_IMPROVEMENT_DECISION["decline_value"]


def next_step_context(phase, light_mode=False):
    interview_mode = "light" if light_mode else "strict"
    messages = {
        "elon_requirements": (
            f"Next required step: Elon Musk (CEO) must run a {interview_mode} requirements interview, "
            "ask enough questions to understand intent, success criteria, constraints, non-goals, "
            "and produce the CEO product brief. When the user approves that brief, advance to CTO planning."
        ),
        "user_brief_approval": "Next required step: wait for explicit user approval of the CEO product brief before CTO planning.",
        "cto_planning": "Next required step: spawn harness-planner as Dario Amodei (CTO) to write 01-planning.md.",
        "ceo_plan_challenge": "Next required step: spawn harness-ceo-plan-challenger as Elon Musk (CEO) to challenge the CTO plan against the user intent.",
        "cto_plan_response": "Next required step: spawn harness-planner as Dario Amodei (CTO) to answer the CEO challenge and update or defend the plan.",
        "user_plan_clarification": "Next required step: wait for the user to answer the CTO clarification, then return to CTO planning.",
        "user_plan_approval": "Next required step: wait for explicit user approval of the CTO plan before implementation.",
        "implementation": "Next required step: spawn harness-implementer as Jeff Dean to implement only the approved plan.",
        "verification": "Next required step: spawn harness-verifier as John von Neumann to write 03-verification-report.md.",
        "reviews": "Next required step: spawn all three reviewers, including Erich Gamma for design-pattern review.",
        "cto_review_triage": "Next required step: spawn harness-planner as Dario Amodei (CTO) to triage Erich Gamma recommendations.",
        "user_improvement_decision": "Next required step: ask the user to apply the CTO-marked design recommendation as rework or decline it before finalization.",
        "rework": "Next required step: send required rework back to implementation, then rerun verification and reviews.",
        "final_elon_check": "Next required step: spawn harness-finalizer as Elon Musk to compare the result against the CEO brief and write 05-final-decision.md.",
        "ready": "Harness task is ready. Report the User Briefing from 05-final-decision.md to the user.",
    }
    return messages.get(phase, f"Next required step: resolve unknown harness phase {phase}.")


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
    print(json.dumps({"additionalContext": message, "message": message}))


def emit_block(message):
    print(
        json.dumps(
            {
                "decision": "block",
                "message": message,
                "additionalContext": message,
            }
        )
    )
    return 1


def emit_allow():
    emit_quiet()
    return 0


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


def repo_root_from(cwd):
    repo_root_output = run_git(["rev-parse", "--show-toplevel"], cwd)
    if not repo_root_output:
        return None
    return pathlib.Path(repo_root_output.strip())


def load_harness_state(repo_root):
    project_codex = repo_root / ".codex"
    current_task_path = project_codex / "current-task"
    if not current_task_path.exists():
        return None, None, {}
    try:
        task_id = current_task_path.read_text(encoding="utf-8", errors="replace").strip().splitlines()[0].strip()
    except (OSError, IndexError):
        return None, None, {}
    if not task_id:
        return None, None, {}
    run_dir = project_codex / "runs" / task_id
    state_path = run_dir / "state.json"
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        state = {}
    return task_id, run_dir, state if isinstance(state, dict) else {}


def write_harness_state(run_dir, state):
    state_path = run_dir / "state.json"
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def create_task_id(prompt_text):
    words = re.findall(r"[A-Za-z0-9가-힣]+", prompt_text.lower())
    slug = "-".join(words[:4]) or "harness-task"
    slug = re.sub(r"[^A-Za-z0-9가-힣-]+", "-", slug).strip("-")[:48] or "harness-task"
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{timestamp}-{slug}"


def ensure_harness_task(repo_root, prompt_text):
    project_codex = repo_root / ".codex"
    current_task_path = project_codex / "current-task"
    task_id, run_dir, state = load_harness_state(repo_root)
    if task_id:
        phase = state.get("phase", "elon_requirements")
        return task_id, run_dir, phase, False

    task_id = create_task_id(prompt_text)
    run_dir = project_codex / "runs" / task_id
    run_dir.mkdir(parents=True, exist_ok=True)
    current_task_path.parent.mkdir(parents=True, exist_ok=True)
    current_task_path.write_text(task_id + "\n", encoding="utf-8")
    state = {
        "task_id": task_id,
        "phase": "elon_requirements",
        "requirements_mode": "light" if is_light_harness_request(prompt_text) else "strict",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    write_harness_state(run_dir, state)
    return task_id, run_dir, "elon_requirements", True


def active_run_without_current_task(project_codex):
    runs_dir = project_codex / "runs"
    if not runs_dir.exists():
        return None
    for state_path in sorted(runs_dir.glob("*/state.json"), key=lambda path: path.stat().st_mtime, reverse=True):
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(state, dict) and state.get("phase") != "ready":
            return state_path.parent.name
    return None


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


def section_text(path, section_name):
    try:
        lines = pathlib.Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""

    in_section = False
    body = []
    for raw_line in lines:
        line = raw_line.strip()
        if line.lower() == f"## {section_name}".lower():
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            body.append(raw_line)
    return "\n".join(body).strip()


def has_meaningful_section(path, section_name):
    text = section_text(path, section_name)
    if not text:
        return False
    for raw_line in text.splitlines():
        line = raw_line.strip("-*`#:\t ").strip()
        if not line:
            continue
        lowered = line.lower()
        if lowered in {"none", "n/a", "na"}:
            continue
        label_only = line.rstrip(":").strip().lower()
        if label_only in PLACEHOLDER_LABELS:
            continue
        if lowered.startswith(("list ", "write ", "use one of:", "for each recommendation")):
            continue
        return True
    return False


def section_contains_token(path, section_name, tokens):
    text = section_text(path, section_name).lower()
    return any(re.search(rf"\b{re.escape(token)}\b", text) for token in tokens)


def path_relative_to(path, root):
    candidate = pathlib.Path(path)
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        return candidate.resolve(strict=False).relative_to(root.resolve(strict=False))
    except ValueError:
        return None


def collect_path_values(value):
    if isinstance(value, dict):
        paths = []
        for key, nested in value.items():
            if key in ("file_path", "filepath", "path", "filename", "target_file", "targetFile"):
                if isinstance(nested, str):
                    paths.append(nested)
            else:
                paths.extend(collect_path_values(nested))
        return paths
    if isinstance(value, list):
        paths = []
        for nested in value:
            paths.extend(collect_path_values(nested))
        return paths
    return []


def collect_patch_paths(text):
    if not isinstance(text, str):
        return []
    paths = []
    for line in text.splitlines():
        match = re.match(r"\*\*\* (?:Add|Update|Delete) File: (.+)", line)
        if not match:
            match = re.match(r"\*\*\* Move to: (.+)", line)
        if match:
            paths.append(match.group(1).strip())
    return paths


def tool_target_paths(payload):
    tool_input = payload.get("tool_input") or payload.get("toolInput") or {}
    paths = collect_path_values(tool_input)
    for value in (payload, tool_input):
        if isinstance(value, dict):
            for key in ("patch", "input", "cmd", "command"):
                paths.extend(collect_patch_paths(value.get(key)))
        elif isinstance(value, str):
            paths.extend(collect_patch_paths(value))
    return sorted(set(path for path in paths if path))


def is_allowed_harness_write(rel_path, task_id, phase):
    rel = rel_path.as_posix()
    if rel == ".codex/current-task":
        return phase in CURRENT_TASK_WRITE_PHASES
    run_prefix = f".codex/runs/{task_id}/"
    if not rel.startswith(run_prefix):
        return False
    run_file = rel[len(run_prefix):]
    if run_file == "state.json":
        return phase != "ready"
    return run_file in PHASE_ALLOWED_HARNESS_REPORTS.get(phase, set())


def update_phase(run_dir, state, phase, extra=None):
    next_state = dict(state)
    next_state["phase"] = phase
    if extra:
        next_state.update(extra)
    next_state["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    write_harness_state(run_dir, next_state)


def handle_user_prompt_submit(_event_name, cwd, payload):
    prompt_text = prompt_text_from(payload)
    repo_root = repo_root_from(cwd)
    if not repo_root:
        if is_harness_request(prompt_text):
            return emit_block(
                "Codex harness mode requires a git repository so hard gates can inspect changed files and task state."
            )
        emit_quiet()
        return 0

    task_id, _run_dir, state = load_harness_state(repo_root)
    if task_id and not is_harness_request(prompt_text):
        phase = state.get("phase", "elon_requirements")
        light_mode = state.get("requirements_mode") == "light"
        if phase == "user_improvement_decision":
            decision = improvement_decision_from_prompt(prompt_text)
            next_phase = {
                REVIEW_IMPROVEMENT_DECISION["decline_value"]: REVIEW_IMPROVEMENT_DECISION["decline_next_phase"],
                REVIEW_IMPROVEMENT_DECISION["rework_value"]: REVIEW_IMPROVEMENT_DECISION["rework_next_phase"],
            }.get(decision)
            if decision and next_phase:
                update_phase(_run_dir, state, next_phase, {REVIEW_IMPROVEMENT_DECISION["state_key"]: decision})
                emit_context(
                    "Codex harness advanced task "
                    f"{task_id} from {phase} to {next_phase}. "
                    f"{next_step_context(next_phase, light_mode)}"
                )
                return 0
        next_phase = USER_CLARIFICATION_TRANSITIONS.get(phase)
        if next_phase and prompt_text.strip():
            update_phase(_run_dir, state, next_phase)
            emit_context(
                "Codex harness advanced task "
                f"{task_id} from {phase} to {next_phase}. "
                f"{next_step_context(next_phase, light_mode)}"
            )
            return 0
        next_phase = USER_APPROVAL_TRANSITIONS.get(phase)
        if next_phase and is_approval_prompt(prompt_text):
            update_phase(_run_dir, state, next_phase)
            emit_context(
                "Codex harness advanced task "
                f"{task_id} from {phase} to {next_phase}. "
                f"{next_step_context(next_phase, light_mode)}"
            )
            return 0
        emit_context(
            "Codex harness active task "
            f"{task_id}. Current phase is {phase}. {next_step_context(phase, light_mode)}"
        )
        return 0

    if not is_harness_request(prompt_text):
        emit_quiet()
        return 0

    try:
        task_id, _run_dir, phase, created = ensure_harness_task(repo_root, prompt_text)
    except OSError as error:
        return emit_block(f"Codex harness could not initialize task state: {error}.")

    action = "created" if created else "found"
    _task_id, _run_dir, state = load_harness_state(repo_root)
    light_mode = state.get("requirements_mode") == "light" or is_light_harness_request(prompt_text)
    emit_context(
        "Codex harness mode "
        f"{action} task {task_id}. Current phase is {phase}. "
        f"{next_step_context(phase, light_mode)}"
    )
    return 0


def handle_pre_tool_use(_event_name, cwd, payload):
    repo_root = repo_root_from(cwd)
    if not repo_root:
        return emit_allow()
    task_id, _run_dir, state = load_harness_state(repo_root)
    if not task_id:
        return emit_allow()

    phase = state.get("phase", "elon_requirements")
    tool_name = payload.get("tool_name") or payload.get("toolName") or payload.get("tool")
    if tool_name in SOURCE_EDIT_TOOLS and phase not in ("implementation", "rework"):
        target_paths = tool_target_paths(payload)
        if target_paths:
            rel_paths = [path_relative_to(path, repo_root) for path in target_paths]
            if all(rel_path is not None and is_allowed_harness_write(rel_path, task_id, phase) for rel_path in rel_paths):
                return emit_allow()
        return emit_block(
            "Codex harness blocked a source edit because the current phase is "
            f"{phase}. Continue the harness flow to the implementation phase before editing files."
        )
    if tool_name in BASH_TOOLS and phase not in BASH_ALLOWED_PHASES:
        return emit_block(
            "Codex harness blocked Bash because the current phase is "
            f"{phase}. Bash is allowed only after the implementation phase starts."
        )

    return emit_allow()


def subagent_type_from(payload):
    for key in ("subagent_type", "subagentType", "agent_type", "agentType", "name"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def report_path_for_key(run_dir, report_key):
    return run_dir / REPORT_DEFINITIONS[report_key]["file"]


def parse_report_status(run_dir, report_key):
    report = REPORT_DEFINITIONS[report_key]
    return parse_section_status(
        report_path_for_key(run_dir, report_key),
        report["section"],
        tuple(report["allowed_statuses"]),
    )


def status_transition_for_phase(phase, run_dir):
    transition = PHASES.get(phase, {}).get("status_transition")
    if not transition:
        return None
    status = parse_report_status(run_dir, transition["report_key"])
    return transition["transitions"].get(status, phase)


def handle_subagent_lifecycle(event_name, cwd, payload):
    repo_root = repo_root_from(cwd)
    if not repo_root:
        return emit_allow()
    task_id, _run_dir, state = load_harness_state(repo_root)
    if not task_id:
        return emit_allow()

    phase = state.get("phase", "elon_requirements")
    subagent_type = subagent_type_from(payload)

    if event_name == "SubagentStart":
        allowed = PHASE_ALLOWED_SUBAGENTS.get(phase, set())
        if subagent_type and subagent_type not in allowed:
            return emit_block(
                "Codex harness blocked subagent "
                f"{subagent_type} during phase {phase}. Allowed subagents: "
                f"{', '.join(sorted(allowed)) or 'none'}."
            )

    if event_name == "SubagentStop":
        if phase in PHASE_REPORT_TRANSITIONS:
            report_name, next_phase = PHASE_REPORT_TRANSITIONS[phase]
            report_path = _run_dir / report_name
            if not report_path.exists():
                return emit_block(
                    "Codex harness blocked phase transition because "
                    f"{report_name} is missing for phase {phase}."
                )
            update_phase(_run_dir, state, next_phase)
            log_dispatch(event_name, cwd, "advanced", f"{phase}_to_{next_phase}")
            return emit_allow()

        if "status_transition" in PHASES.get(phase, {}):
            report_key = PHASES[phase]["status_transition"]["report_key"]
            report_path = report_path_for_key(_run_dir, report_key)
            if not report_path.exists():
                return emit_block(
                    "Codex harness blocked phase transition because "
                    f"{report_path.name} is missing for phase {phase}."
                )
            if phase == "final_elon_check":
                final_policy = COMPLETION_POLICY["final_decision"]
                if not has_meaningful_section(report_path, final_policy["user_briefing_section"]):
                    return emit_block(
                        "Codex harness blocked phase transition because "
                        f"{report_path.name} is missing a meaningful {final_policy['user_briefing_section']} section."
                    )
            next_phase = status_transition_for_phase(phase, _run_dir)
            update_phase(_run_dir, state, next_phase)
            log_dispatch(event_name, cwd, "advanced", f"{phase}_to_{next_phase}")
            return emit_allow()

        if phase == "reviews":
            expected_report = REVIEW_REPORTS_BY_SUBAGENT.get(subagent_type)
            if expected_report and not (_run_dir / expected_report).exists():
                return emit_block(
                    "Codex harness blocked phase transition because "
                    f"{expected_report} is missing for subagent {subagent_type}."
                )
            required_review_keys = tuple(REVIEW_GATE["required_reports"])
            if all(report_path_for_key(_run_dir, key).exists() for key in required_review_keys):
                next_phase = REVIEW_GATE["next_phase_when_passed"]
                for key in required_review_keys:
                    status = parse_report_status(_run_dir, key)
                    if status not in REPORT_DEFINITIONS[key]["completion_passes"]:
                        next_phase = REVIEW_GATE["next_phase_when_blocked"]
                        break
                update_phase(_run_dir, state, next_phase)
                log_dispatch(event_name, cwd, "advanced", f"{phase}_to_{next_phase}")
                return emit_allow()

    reason = "subagent_started" if event_name == "SubagentStart" else "subagent_stopped"
    log_dispatch(event_name, cwd, "allowed", reason)
    return emit_allow()


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
        active_task = active_run_without_current_task(project_codex)
        if active_task:
            log_dispatch(event_name, cwd, "blocked", "missing_current_task_for_active_run")
            append_stop_log(event_name, cwd, True, len(paths), "blocked", "missing_current_task_for_active_run")
            return emit_block(
                "Codex harness blocked completion: .codex/current-task is missing while "
                f"active harness run {active_task} still exists."
            )
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
        active_task = active_run_without_current_task(project_codex)
        if active_task:
            log_dispatch(event_name, cwd, "blocked", "empty_current_task_for_active_run")
            append_stop_log(event_name, cwd, True, len(paths), "blocked", "empty_current_task_for_active_run")
            return emit_block(
                "Codex harness blocked completion: .codex/current-task is empty while "
                f"active harness run {active_task} still exists."
            )
        log_dispatch(event_name, cwd, "warning", "empty_current_task")
        append_stop_log(event_name, cwd, True, len(paths), "warning", "empty_current_task")
        emit_context("Codex harness warning: .codex/current-task is empty.")
        return 0

    run_dir = project_codex / "runs" / task_id
    _task_id, _run_dir, state = load_harness_state(repo_root)
    reports = {
        key: run_dir / report["file"]
        for key, report in REPORT_DEFINITIONS.items()
        if report.get("required_for_completion", True)
    }

    missing = [name for name, path in reports.items() if not path.exists()]
    if missing:
        log_dispatch(event_name, cwd, "blocked", "missing_reports")
        append_stop_log(event_name, cwd, True, len(paths), "blocked", "missing_reports")
        return emit_block(
            "Codex harness blocked completion: missing reports for task "
            f"{task_id}: {', '.join(missing)}."
        )

    statuses = {
        key: parse_section_status(path, report["section"], tuple(report["allowed_statuses"]))
        for key, path in reports.items()
        for report in (REPORT_DEFINITIONS[key],)
        if "section" in report
    }

    warnings = []
    for key, status in statuses.items():
        report = REPORT_DEFINITIONS[key]
        if key == "cto-review-triage":
            continue
        if status not in report.get("completion_passes", []):
            warnings.append(f"{report['warning_key']}={status or 'unknown'}")

    cto_triage = statuses.get("cto-review-triage")
    cto_triage_passes = cto_triage in REPORT_DEFINITIONS["cto-review-triage"]["completion_passes"] or (
        cto_triage == "needs_user_decision" and user_declined_improvement(state)
    )
    if not cto_triage_passes:
        warnings.append(f"cto_triage={cto_triage or 'unknown'}")

    final_policy = COMPLETION_POLICY["final_decision"]
    if not has_meaningful_section(reports["final-decision"], final_policy["user_briefing_section"]):
        warnings.append(final_policy["user_briefing_warning_key"])

    design_policy = COMPLETION_POLICY["design_improvement"]
    if statuses.get("review-design-patterns") == design_policy["status"]:
        triage_path = reports["cto-review-triage"]
        decisions_section = design_policy["decisions_section"]
        if not has_meaningful_section(triage_path, design_policy["recommendations_reviewed_section"]):
            warnings.append(design_policy["recommendations_reviewed_warning_key"])
        if not has_meaningful_section(triage_path, decisions_section):
            warnings.append(design_policy["decisions_warning_key"])
        if section_contains_token(triage_path, decisions_section, (design_policy["must_apply_token"],)):
            warnings.append(design_policy["must_apply_warning_key"])
        if section_contains_token(triage_path, decisions_section, (design_policy["user_decision_token"],)):
            if user_declined_improvement(state):
                try:
                    final_text = reports["final-decision"].read_text(encoding="utf-8", errors="replace").lower()
                except OSError:
                    final_text = ""
                if final_policy["user_declined_required_token"] not in final_text:
                    warnings.append(final_policy["user_declined_warning_key"])
            else:
                warnings.append(design_policy["user_decision_warning_key"])
        if section_contains_token(triage_path, decisions_section, (design_policy["declined_by_cto_token"],)):
            if not section_contains_token(
                triage_path,
                design_policy["declined_reasons_section"],
                design_policy["declined_reason_values"],
            ):
                warnings.append(design_policy["declined_reason_warning_key"])
            try:
                final_text = reports["final-decision"].read_text(encoding="utf-8", errors="replace").lower()
            except OSError:
                final_text = ""
            if not any(reason in final_text for reason in design_policy["declined_reason_values"]):
                warnings.append(design_policy["final_declined_reason_warning_key"])

    if warnings:
        log_dispatch(event_name, cwd, "blocked", "reports_not_ready")
        append_stop_log(event_name, cwd, True, len(paths), "blocked", "reports_not_ready")
        return emit_block(
            "Codex harness blocked completion: task "
            f"{task_id} is not ready ({'; '.join(warnings)})."
        )

    log_dispatch(event_name, cwd, "ready", "reports_ready")
    append_stop_log(event_name, cwd, True, len(paths), "ready", "reports_ready")
    cleanup_runtime_logs()
    emit_context(f"Codex harness ready: task {task_id} has passed verification, all reviews, and CTO triage.")
    return 0


def main():
    payload = load_payload()
    event_name = event_name_from(payload)
    cwd = cwd_from(payload)

    if event_name == "UserPromptSubmit":
        return handle_user_prompt_submit(event_name, cwd, payload)
    if event_name == "PreToolUse":
        return handle_pre_tool_use(event_name, cwd, payload)
    if event_name in ("SubagentStart", "SubagentStop"):
        return handle_subagent_lifecycle(event_name, cwd, payload)
    if event_name == "Stop":
        return handle_stop(event_name, cwd)

    log_dispatch(event_name, cwd, "silent", "unsupported_event")
    emit_quiet()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
