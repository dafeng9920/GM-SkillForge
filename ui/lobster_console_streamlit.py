from __future__ import annotations

import concurrent.futures as cf
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
DISPATCH_DIR = ROOT / ".tmp" / "openclaw-dispatch"
DEFAULT_BASELINE = "AG2-FIXED-CALIBER-TG1-20260304"
DEFAULT_HOST = "BlueLobster-Cloud"
DEFAULT_USER = "root"
DEFAULT_REPO = "/root/gm-skillforge"


def now_task_id() -> str:
    return "r1-cloud-smoke-" + dt.datetime.now().strftime("%Y%m%d-%H%M")


def objective_from_task_id(task_id: str) -> str:
    tid = (task_id or "").strip().lower()
    if tid.startswith("m2-outer-parity-"):
        return "M2 外螺旋语义 parity 回归"
    if tid.startswith("m3-inner-parity-"):
        return "M3 内螺旋健康审计 parity 回归"
    if tid.startswith("m4-beidou-parity-"):
        return "M4 北斗可观测语义 parity 回归"
    if tid.startswith("r1-cloud-smoke-"):
        return "R1 CLOUD-ROOT 基础链路回归（目录/版本/资源）"
    return ""


def resolve_objective(task_id: str, fallback: str) -> str:
    return objective_from_task_id(task_id) or fallback

def build_task_id(prefix: str) -> str:
    return f"{prefix}-{dt.datetime.now().strftime('%Y%m%d')}-01"


def preset_map() -> dict[str, dict[str, str]]:
    today_dir = f"docs/{dt.datetime.now().strftime('%Y-%m-%d')}/verification"
    return {
        "R1 CLOUD-ROOT 基础回归": {
            "task_id": now_task_id(),
            "baseline_id": DEFAULT_BASELINE,
            "objective": "R1 CLOUD-ROOT 基础链路回归（目录/版本/资源）",
            "cloud_host": DEFAULT_HOST,
            "cloud_user": DEFAULT_USER,
            "cloud_repo": DEFAULT_REPO,
            "verification_dir": today_dir,
        },
        "M2 外螺旋 parity": {
            "task_id": build_task_id("m2-outer-parity"),
            "baseline_id": DEFAULT_BASELINE,
            "objective": "M2 外螺旋语义 parity 回归",
            "cloud_host": DEFAULT_HOST,
            "cloud_user": DEFAULT_USER,
            "cloud_repo": DEFAULT_REPO,
            "verification_dir": today_dir,
        },
        "M3 内螺旋 parity": {
            "task_id": build_task_id("m3-inner-parity"),
            "baseline_id": DEFAULT_BASELINE,
            "objective": "M3 内螺旋健康审计 parity 回归",
            "cloud_host": DEFAULT_HOST,
            "cloud_user": DEFAULT_USER,
            "cloud_repo": DEFAULT_REPO,
            "verification_dir": today_dir,
        },
        "M4 北斗 parity": {
            "task_id": build_task_id("m4-beidou-parity"),
            "baseline_id": DEFAULT_BASELINE,
            "objective": "M4 北斗可观测语义 parity 回归",
            "cloud_host": DEFAULT_HOST,
            "cloud_user": DEFAULT_USER,
            "cloud_repo": DEFAULT_REPO,
            "verification_dir": today_dir,
        },
    }


def run_cmd(cmd: list[str], timeout_sec: int = 180) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
        output = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
        return proc.returncode, output.strip()
    except subprocess.TimeoutExpired:
        return 124, f"命令超时（{timeout_sec}s）: {' '.join(cmd)}"


def parse_status_json(output: str) -> dict | None:
    """Parse the first JSON object line from lobsterctl status output."""
    if not output:
        return None
    for line in output.splitlines():
        s = line.strip()
        if not (s.startswith("{") and s.endswith("}")):
            continue
        try:
            obj = json.loads(s)
            if isinstance(obj, dict) and "state" in obj:
                return obj
        except json.JSONDecodeError:
            continue
    return None


def ensure_contract(task_id: str, baseline_id: str, objective: str) -> Path:
    task_dir = DISPATCH_DIR / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    contract = {
        "task_id": task_id,
        "baseline_id": baseline_id,
        "objective": objective,
        "environment": "CLOUD-ROOT",
        "constraints": {"fail_closed": True},
        "policy": {"max_commands": 6},
        "command_allowlist": [
            "cd /root/gm-skillforge",
            "pwd",
            "python3 --version",
            "df -h",
            "free -m",
            "uptime",
        ],
        "required_artifacts": [
            "execution_receipt.json",
            "stdout.log",
            "stderr.log",
            "audit_event.json",
        ],
        "acceptance": [
            "execution_receipt.status == success",
            "execution_receipt.exit_code == 0",
            "executed_commands are a subset of command_allowlist",
            "required_artifacts are complete",
        ],
    }
    path = task_dir / "task_contract.json"
    path.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def lobsterctl(*args: str) -> tuple[int, str]:
    cmd = [sys.executable, str(ROOT / "scripts" / "lobsterctl.py"), *args]
    timeout_map = {
        "submit": 90,
        "fetch": 240,
        "status": 60,
        "verify": 120,
        "prepare": 60,
    }
    action = args[0] if args else ""
    return run_cmd(cmd, timeout_sec=timeout_map.get(action, 180))

def execute_action(
    action: str,
    *,
    task_id: str,
    baseline_id: str,
    objective: str,
    cloud_host: str,
    cloud_user: str,
    cloud_repo: str,
    verification_dir: str,
) -> tuple[int, str]:
    if action == "prepare":
        contract_path = ensure_contract(task_id, baseline_id, objective)
        return 0, f"Contract ready: {contract_path}"
    if action == "submit":
        return lobsterctl(
            "submit",
            "--task-id",
            task_id,
            "--cloud-host",
            cloud_host,
            "--cloud-user",
            cloud_user,
            "--cloud-repo",
            cloud_repo,
        )
    if action == "status":
        return lobsterctl(
            "status",
            "--task-id",
            task_id,
            "--cloud-host",
            cloud_host,
            "--cloud-user",
            cloud_user,
            "--cloud-repo",
            cloud_repo,
        )
    if action == "fetch":
        return lobsterctl(
            "fetch",
            "--task-id",
            task_id,
            "--cloud-host",
            cloud_host,
            "--cloud-user",
            cloud_user,
            "--cloud-repo",
            cloud_repo,
        )
    if action == "verify":
        return lobsterctl(
            "verify",
            "--task-id",
            task_id,
            "--verification-dir",
            verification_dir,
        )
    return 2, f"Unsupported action: {action}"


def infer_action_from_text(text: str) -> str:
    t = text.strip().lower()
    if any(k in t for k in ["准备", "合同", "prepare", "contract"]):
        return "prepare"
    if any(k in t for k in ["提交", "下发", "submit", "dispatch"]):
        return "submit"
    if any(k in t for k in ["状态", "进度", "status", "log"]):
        return "status"
    if any(k in t for k in ["获取", "回收", "fetch", "artifact"]):
        return "fetch"
    if any(k in t for k in ["核实", "复验", "verify", "gate"]):
        return "verify"
    if any(k in t for k in ["继续", "刚才", "上一单", "continue", "resume"]):
        return "status"
    return ""


def extract_task_id_from_text(text: str) -> str:
    patterns = [
        r"task[_\s-]?id\s*[:=]\s*([A-Za-z0-9][A-Za-z0-9\-]{5,})",
        r"任务id\s*[:：]\s*([A-Za-z0-9][A-Za-z0-9\-]{5,})",
        r"任务\s*[:：]\s*([A-Za-z0-9][A-Za-z0-9\-]{5,})",
    ]
    for p in patterns:
        m = re.search(p, text, flags=re.IGNORECASE)
        if m:
            return m.group(1)
    return ""

def on_task_id_change() -> None:
    task_id = st.session_state.ui_task_id
    st.session_state.active_task_id = task_id
    st.session_state.last_task_id = task_id
    st.session_state.last_action = "status"
    st.session_state.last_result = None
    suggested_objective = objective_from_task_id(task_id)
    if suggested_objective:
        st.session_state.ui_objective = suggested_objective
    st.session_state.task_switch_notice = f"已切换到任务：{task_id}（旧任务输出已清空）"


def on_apply_preset() -> None:
    presets = preset_map()
    selected = st.session_state.get("ui_preset_choice", "")
    if not selected or selected not in presets:
        return
    p = presets[selected]
    st.session_state.ui_task_id = p["task_id"]
    st.session_state.ui_baseline_id = p["baseline_id"]
    st.session_state.ui_objective = p["objective"]
    st.session_state.ui_cloud_host = p["cloud_host"]
    st.session_state.ui_cloud_user = p["cloud_user"]
    st.session_state.ui_cloud_repo = p["cloud_repo"]
    st.session_state.ui_verification_dir = p["verification_dir"]
    st.session_state.active_task_id = p["task_id"]
    st.session_state.last_task_id = p["task_id"]
    st.session_state.last_action = "status"
    st.session_state.last_result = None
    st.session_state.task_switch_notice = f"已套用模板：{selected}（参数已一键填充）"


st.set_page_config(page_title="Lobster Control Console", layout="wide")
st.title("Lobster Control Console (Streamlit)")
st.caption("Submit / Status / Fetch / Verify for CLOUD-ROOT closed-loop tasks")

if "ui_task_id" not in st.session_state:
    st.session_state.ui_task_id = now_task_id()
if "ui_baseline_id" not in st.session_state:
    st.session_state.ui_baseline_id = DEFAULT_BASELINE
if "ui_objective" not in st.session_state:
    st.session_state.ui_objective = "R1 CLOUD-ROOT 基础链路回归（目录/版本/资源）"
if "ui_cloud_host" not in st.session_state:
    st.session_state.ui_cloud_host = DEFAULT_HOST
if "ui_cloud_user" not in st.session_state:
    st.session_state.ui_cloud_user = DEFAULT_USER
if "ui_cloud_repo" not in st.session_state:
    st.session_state.ui_cloud_repo = DEFAULT_REPO
if "ui_verification_dir" not in st.session_state:
    st.session_state.ui_verification_dir = f"docs/{dt.datetime.now().strftime('%Y-%m-%d')}/verification"
if "active_task_id" not in st.session_state:
    st.session_state.active_task_id = st.session_state.ui_task_id
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []
if "last_task_id" not in st.session_state:
    st.session_state.last_task_id = st.session_state.ui_task_id
if "last_action" not in st.session_state:
    st.session_state.last_action = "status"
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "task_switch_notice" not in st.session_state:
    st.session_state.task_switch_notice = ""
if "ui_preset_choice" not in st.session_state:
    st.session_state.ui_preset_choice = "R1 CLOUD-ROOT 基础回归"
if "status_snapshots" not in st.session_state:
    st.session_state.status_snapshots = {}

with st.sidebar:
    st.subheader("Task Settings")
    st.selectbox(
        "任务模板",
        options=list(preset_map().keys()),
        key="ui_preset_choice",
    )
    st.button("一键填充模板参数", on_click=on_apply_preset, use_container_width=True)
    task_id = st.text_input("Task ID", key="ui_task_id", on_change=on_task_id_change)
    baseline_id = st.text_input("Baseline ID", key="ui_baseline_id")
    objective = st.text_input("Objective", key="ui_objective")
    cloud_host = st.text_input("Cloud Host", key="ui_cloud_host")
    cloud_user = st.text_input("Cloud User", key="ui_cloud_user")
    cloud_repo = st.text_input("Cloud Repo", key="ui_cloud_repo")
    verification_dir = st.text_input("Verification Dir", key="ui_verification_dir")

if st.session_state.task_switch_notice:
    st.info(st.session_state.task_switch_notice)
    st.session_state.task_switch_notice = ""


def run_action_ui(action: str, target_task_id: str) -> None:
    code, out = execute_action(
        action,
        task_id=target_task_id,
        baseline_id=baseline_id,
        objective=objective,
        cloud_host=cloud_host,
        cloud_user=cloud_user,
        cloud_repo=cloud_repo,
        verification_dir=verification_dir,
    )
    st.session_state.last_task_id = target_task_id
    st.session_state.last_action = action
    st.session_state.last_result = {
        "task_id": target_task_id,
        "action": action,
        "code": code,
        "output": out or "(no output)",
        "time": dt.datetime.now().strftime("%H:%M:%S"),
    }
    if action == "status":
        parsed = parse_status_json(out or "")
        if parsed is not None:
            st.session_state.status_snapshots[target_task_id] = parsed


def run_quick_prepare_submit_status(target_task_id: str) -> None:
    steps = ["prepare", "submit", "status"]
    outputs: list[str] = []
    final_code = 0
    for step in steps:
        code, out = execute_action(
            step,
            task_id=target_task_id,
            baseline_id=baseline_id,
            objective=objective,
            cloud_host=cloud_host,
            cloud_user=cloud_user,
            cloud_repo=cloud_repo,
            verification_dir=verification_dir,
        )
        outputs.append(f"[{step}] exit={code}\n{out or '(no output)'}")
        final_code = code
        if step == "status":
            parsed = parse_status_json(out or "")
            if parsed is not None:
                st.session_state.status_snapshots[target_task_id] = parsed
        if code != 0:
            break

    st.session_state.last_task_id = target_task_id
    st.session_state.last_action = "quick_prepare_submit_status"
    st.session_state.last_result = {
        "task_id": target_task_id,
        "action": "quick_prepare_submit_status",
        "code": final_code,
        "output": "\n\n".join(outputs),
        "time": dt.datetime.now().strftime("%H:%M:%S"),
    }


def run_action_batch(
    action: str,
    task_ids: list[str],
    *,
    baseline_id: str,
    objective: str,
    cloud_host: str,
    cloud_user: str,
    cloud_repo: str,
    verification_dir: str,
    auto_prepare_before_submit: bool = False,
) -> list[dict[str, str | int]]:
    if not task_ids:
        return []
    if action == "submit" and auto_prepare_before_submit:
        for tid in task_ids:
            ensure_contract(tid, baseline_id, resolve_objective(tid, objective))

    def _worker(tid: str) -> dict[str, str | int]:
        code, out = execute_action(
            action,
            task_id=tid,
            baseline_id=baseline_id,
            objective=resolve_objective(tid, objective),
            cloud_host=cloud_host,
            cloud_user=cloud_user,
            cloud_repo=cloud_repo,
            verification_dir=verification_dir,
        )
        return {"task_id": tid, "code": code, "output": out or "(no output)"}

    max_workers = min(4, max(1, len(task_ids)))
    results: list[dict[str, str | int]] = []
    with cf.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(_worker, tid) for tid in task_ids]
        for fut in cf.as_completed(futures):
            results.append(fut.result())
    results.sort(key=lambda x: str(x["task_id"]))
    return results

quick_col, col1, col2, col3, col4, col5 = st.columns(6)

if quick_col.button("0) 一键准备并提交（含状态）", use_container_width=True):
    run_quick_prepare_submit_status(task_id)

if col1.button("1) Prepare Contract", use_container_width=True):
    run_action_ui("prepare", task_id)

if col2.button("2) Submit", use_container_width=True):
    run_action_ui("submit", task_id)

if col3.button("3) Status", use_container_width=True):
    run_action_ui("status", task_id)

if col4.button("4) Fetch", use_container_width=True):
    run_action_ui("fetch", task_id)

if col5.button("5) Verify", use_container_width=True):
    run_action_ui("verify", task_id)

if st.session_state.last_result and st.session_state.last_result["task_id"] == task_id:
    lr = st.session_state.last_result
    st.code(lr["output"])
    if lr["code"] == 0:
        st.success(f"{lr['action']} 成功（任务 {lr['task_id']}）")
    else:
        st.error(f"{lr['action']} 失败：退出代码 {lr['code']}（任务 {lr['task_id']}）")

status_snapshot = st.session_state.status_snapshots.get(task_id)
with st.expander("状态真值检查（可关机条件）", expanded=False):
    c1, c2 = st.columns(2)
    if c1.button("检查 state=EXITED", use_container_width=True):
        if not status_snapshot:
            st.warning("未找到本任务最近状态快照，请先点一次 3) 状态")
        else:
            v = str(status_snapshot.get("state", ""))
            if v == "EXITED":
                st.success(f"TRUE: state={v}")
            else:
                st.error(f"FALSE: state={v}")
    if c2.button("检查 log_exists=true", use_container_width=True):
        if not status_snapshot:
            st.warning("未找到本任务最近状态快照，请先点一次 3) 状态")
        else:
            v = bool(status_snapshot.get("log_exists", False))
            if v:
                st.success("TRUE: log_exists=true")
            else:
                st.error("FALSE: log_exists=false")
    if status_snapshot:
        st.caption(f"当前快照：state={status_snapshot.get('state')} | log_exists={status_snapshot.get('log_exists')} | log_size={status_snapshot.get('log_size')}")

st.markdown("---")
st.subheader("多任务并行（Swarm）")
st.caption("每行一个 task_id，可并行执行提交/状态/获取/核实。")
default_batch = "\n".join(
    [
        f"m2-outer-parity-{dt.datetime.now().strftime('%Y%m%d')}-01",
        f"m3-inner-parity-{dt.datetime.now().strftime('%Y%m%d')}-01",
        f"m4-beidou-parity-{dt.datetime.now().strftime('%Y%m%d')}-01",
    ]
)
batch_text = st.text_area("任务列表（并行）", value=default_batch, height=90)
batch_task_ids = [x.strip() for x in batch_text.splitlines() if x.strip()]
auto_prepare = st.checkbox("并行提交前自动准备合同", value=True)
b1, b2, b3, b4 = st.columns(4)


def render_batch_results(action_name: str, results: list[dict[str, str | int]]) -> None:
    if not results:
        st.warning("任务列表为空")
        return
    ok = sum(1 for r in results if int(r["code"]) == 0)
    fail = len(results) - ok
    st.write(f"并行{action_name}完成：成功 {ok} / 失败 {fail}")
    rows = [{"task_id": r["task_id"], "exit_code": r["code"]} for r in results]
    st.table(rows)
    for r in results:
        with st.expander(f"{action_name}输出 - {r['task_id']} (exit {r['code']})"):
            st.code(str(r["output"]))


if b1.button("并行提交", use_container_width=True):
    results = run_action_batch(
        "submit",
        batch_task_ids,
        baseline_id=baseline_id,
        objective=objective,
        cloud_host=cloud_host,
        cloud_user=cloud_user,
        cloud_repo=cloud_repo,
        verification_dir=verification_dir,
        auto_prepare_before_submit=auto_prepare,
    )
    render_batch_results("提交", results)

if b2.button("并行状态", use_container_width=True):
    results = run_action_batch(
        "status",
        batch_task_ids,
        baseline_id=baseline_id,
        objective=objective,
        cloud_host=cloud_host,
        cloud_user=cloud_user,
        cloud_repo=cloud_repo,
        verification_dir=verification_dir,
    )
    render_batch_results("状态", results)

if b3.button("并行获取", use_container_width=True):
    results = run_action_batch(
        "fetch",
        batch_task_ids,
        baseline_id=baseline_id,
        objective=objective,
        cloud_host=cloud_host,
        cloud_user=cloud_user,
        cloud_repo=cloud_repo,
        verification_dir=verification_dir,
    )
    render_batch_results("获取", results)

if b4.button("并行核实", use_container_width=True):
    results = run_action_batch(
        "verify",
        batch_task_ids,
        baseline_id=baseline_id,
        objective=objective,
        cloud_host=cloud_host,
        cloud_user=cloud_user,
        cloud_repo=cloud_repo,
        verification_dir=verification_dir,
    )
    render_batch_results("核实", results)

st.markdown("---")
st.subheader("对话指令（给小龙虾）")
st.caption("输入示例：准备合同 / 提交任务 / 查看状态 / 获取回执 / 立即核实")

user_cmd = st.text_input("指令输入框", value="")
if st.button("发送指令", use_container_width=True):
    cmd_task_id = extract_task_id_from_text(user_cmd)
    effective_task_id = cmd_task_id or st.session_state.last_task_id or task_id
    action = infer_action_from_text(user_cmd)
    if not action:
        if any(k in user_cmd.lower() for k in ["继续", "刚才", "上一单", "continue", "resume"]):
            action = st.session_state.last_action or "status"
        else:
            st.warning("无法识别指令。请使用：准备合同/提交/状态/获取/核实，或附带 task_id=xxx")
            action = ""
    if action:
        code, out = execute_action(
            action,
            task_id=effective_task_id,
            baseline_id=baseline_id,
            objective=objective,
            cloud_host=cloud_host,
            cloud_user=cloud_user,
            cloud_repo=cloud_repo,
            verification_dir=verification_dir,
        )
        if code == 0:
            st.session_state.last_task_id = effective_task_id
            st.session_state.last_action = action
            st.success(f"已执行：{action} (task_id={effective_task_id})")
        else:
            st.error(f"执行失败：{action} (task_id={effective_task_id}, exit {code})")
        st.session_state.last_result = {
            "task_id": effective_task_id,
            "action": action,
            "code": code,
            "output": out or "(no output)",
            "time": dt.datetime.now().strftime("%H:%M:%S"),
        }
        if action == "status":
            parsed = parse_status_json(out or "")
            if parsed is not None:
                st.session_state.status_snapshots[effective_task_id] = parsed

        st.session_state.chat_log.append(
            {
                "time": dt.datetime.now().strftime("%H:%M:%S"),
                "user": user_cmd,
                "task_id": effective_task_id,
                "action": action,
                "code": code,
                "reply": out or "(no output)",
            }
        )

if st.session_state.last_task_id:
    st.caption(f"当前会话任务: {st.session_state.last_task_id} | 上次动作: {st.session_state.last_action}")

if st.session_state.chat_log:
    for item in reversed(st.session_state.chat_log[-10:]):
        st.markdown(f"**[{item['time']}] 你：** {item['user']}")
        st.markdown(f"**任务：** `{item['task_id']}`")
        st.markdown(f"**小龙虾：** `{item['action']}` (exit {item['code']})")
        st.code(item["reply"])
        st.markdown("---")

st.subheader("Quick Start")
st.code(
    "streamlit run ui/lobster_console_streamlit.py",
    language="bash",
)
st.subheader("启动命令（PowerShell）")
st.code(
    "& D:\\GM-SkillForge\\.venv\\Scripts\\Activate.ps1\n"
    "python -m pip install -r requirements.txt\n"
    "python -m streamlit run ui/lobster_console_streamlit.py",
    language="powershell",
)
st.write("Tip: Run `Prepare Contract` first, then `Submit`, then `Status`/`Fetch`/`Verify`.")
