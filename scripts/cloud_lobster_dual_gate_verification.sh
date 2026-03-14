#!/bin/bash
#
# Cloud Lobster Dual Gate Verification (LOCAL-ANTIGRAVITY)
#
# 用途：在 LOCAL-ANTIGRAVITY 环境运行双重门禁复验
#
# 双重门禁：
#   1. verify_execution_receipt.py - 回执校验
#   2. cloud_lobster_mandatory_gate.py - 强制门禁
#
# 目标：2/2 PASS
#

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

log_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# 检查环境
check_environment() {
    log_info "检查 LOCAL-ANTIGRAVITY 环境..."

    # 检查 Python
    if ! command -v python &> /dev/null; then
        log_error "Python 未找到"
        exit 1
    fi

    # 检查脚本存在
    if [[ ! -f "scripts/verify_execution_receipt.py" ]]; then
        log_error "verify_execution_receipt.py 未找到"
        exit 1
    fi

    if [[ ! -f "scripts/cloud_lobster_mandatory_gate.py" ]]; then
        log_error "cloud_lobster_mandatory_gate.py 未找到"
        exit 1
    fi

    log_success "LOCAL-ANTIGRAVITY 环境检查通过"
}

# 门禁 1：回执校验
gate1_verify_receipt() {
    local task_id=$1
    local task_dir=".tmp/openclaw-dispatch/${task_id}"
    local contract_file="${task_dir}/task_contract.json"
    local receipt_file="${task_dir}/execution_receipt.json"

    log_step "门禁 1/2: 回执校验 (verify_execution_receipt.py)"

    # 检查文件存在
    if [[ ! -f "$contract_file" ]]; then
        log_error "任务合同不存在: $contract_file"
        return 1
    fi

    if [[ ! -f "$receipt_file" ]]; then
        log_error "执行回执不存在: $receipt_file"
        return 1
    fi

    # 运行验证
    log_info "运行 verify_execution_receipt.py..."
    local output
    output=$(python skills/openclaw-cloud-bridge-skill/scripts/verify_execution_receipt.py \
        --contract "$contract_file" \
        --receipt "$receipt_file" \
        --quiet 2>&1)
    local result=$?

    if [[ $result -eq 0 && "$output" == "PASS" ]]; then
        log_success "门禁 1/2: PASS ✓"
        return 0
    else
        log_error "门禁 1/2: FAIL ✗"
        echo "$output"
        return 1
    fi
}

# 门禁 2：强制门禁
gate2_mandatory_gate() {
    local task_id=$1

    log_step "门禁 2/2: 强制门禁 (cloud_lobster_mandatory_gate.py)"

    # 运行强制门禁
    log_info "运行 cloud_lobster_mandatory_gate.py..."
    local output
    output=$(python scripts/cloud_lobster_mandatory_gate.py \
        --task-id "$task_id" \
        --quiet 2>&1)
    local result=$?

    # 判定：退出码为 0 即 PASS (ALLOW), 非 0 即 FAIL (DENY)
    if [[ $result -eq 0 ]]; then
        log_success "门禁 2/2: PASS ✓"
        return 0
    else
        log_error "门禁 2/2: FAIL ✗"
        echo "$output"
        return 1
    fi
}

# 显示详细结果
show_detailed_results() {
    local task_id=$1
    local task_dir=".tmp/openclaw-dispatch/${task_id}"

    echo ""
    echo "=========================================="
    echo "详细结果"
    echo "=========================================="

    # 门禁 1 详细结果
    echo ""
    log_step "门禁 1: 回执校验详情"
    python skills/openclaw-cloud-bridge-skill/scripts/verify_execution_receipt.py \
        --contract "${task_dir}/task_contract.json" \
        --receipt "${task_dir}/execution_receipt.json" \
        2>&1 || true

    # 门禁 2 详细结果
    echo ""
    log_step "门禁 2: 强制门禁详情"
    python scripts/cloud_lobster_mandatory_gate.py \
        --task-id "$task_id" \
        2>&1 || true

    echo ""
    echo "=========================================="
}

# 生成结果报告
generate_result_report() {
    local task_id=$1
    local gate1_result=$2
    local gate2_result=$3
    local report_file="docs/2026-03-05/dual_gate_report_${task_id}.json"

    log_info "生成结果报告: $report_file"

    mkdir -p "docs/2026-03-05"

    cat > "$report_file" << EOF
{
  "report_type": "dual_gate_verification",
  "task_id": "$task_id",
  "generated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "execution_environment": "LOCAL-ANTIGRAVITY",
  "verification_target": "2/2 PASS",
  "results": {
    "gate1_receipt_verification": {
      "name": "verify_execution_receipt.py",
      "status": "$([ $gate1_result -eq 0 ] && echo "PASS" || echo "FAIL")",
      "exit_code": $gate1_result
    },
    "gate2_mandatory_gate": {
      "name": "cloud_lobster_mandatory_gate.py",
      "status": "$([ $gate2_result -eq 0 ] && echo "PASS" || echo "FAIL")",
      "exit_code": $gate2_result
    }
  },
  "summary": {
    "total_gates": 2,
    "passed": $(( ($gate1_result == 0 ? 1 : 0) + ($gate2_result == 0 ? 1 : 0) )),
    "failed": $(( ($gate1_result != 0 ? 1 : 0) + ($gate2_result != 0 ? 1 : 0) )),
    "overall": "$([ $gate1_result -eq 0 ] && [ $gate2_result -eq 0 ] && echo "PASS" || echo "FAIL")"
  },
  "compliance": {
    "target_met": "$([ $gate1_result -eq 0 ] && [ $gate2_result -eq 0 ] && echo "true" || echo "false")",
    "target": "2/2 PASS",
    "actual": "$(( ($gate1_result == 0 ? 1 : 0) + ($gate2_result == 0 ? 1 : 0) ))/2 PASS"
  }
}
EOF

    log_success "结果报告已生成"
}

# 主函数
main() {
    local task_id=$1

    if [[ -z "$task_id" ]]; then
        log_error "用法: $0 <task-id>"
        log_error "示例: $0 cl-demo-20260305-0800"
        exit 1
    fi

    echo "=========================================="
    echo "Cloud Lobster Dual Gate Verification"
    echo "(LOCAL-ANTIGRAVITY)"
    echo "=========================================="
    echo "Task ID: $task_id"
    echo "Target: 2/2 PASS"
    echo "Started at: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "=========================================="
    echo ""

    # 检查环境
    check_environment

    # 门禁 1：回执校验
    gate1_result=0
    if ! gate1_verify_receipt "$task_id"; then
        gate1_result=1
    fi

    # 门禁 2：强制门禁
    gate2_result=0
    if ! gate2_mandatory_gate "$task_id"; then
        gate2_result=1
    fi

    # 计算总体结果
    echo ""
    echo "=========================================="
    echo "双重门禁复验结果"
    echo "=========================================="

    if [[ $gate1_result -eq 0 && $gate2_result -eq 0 ]]; then
        echo -e "${GREEN}✓ 门禁 1/2: PASS${NC}"
        echo -e "${GREEN}✓ 门禁 2/2: PASS${NC}"
        echo ""
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}✓✓✓ 2/2 PASS - 目标达成 ✓✓✓${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    else
        if [[ $gate1_result -ne 0 ]]; then
            echo -e "${RED}✗ 门禁 1/2: FAIL${NC}"
        else
            echo -e "${GREEN}✓ 门禁 1/2: PASS${NC}"
        fi

        if [[ $gate2_result -ne 0 ]]; then
            echo -e "${RED}✗ 门禁 2/2: FAIL${NC}"
        else
            echo -e "${GREEN}✓ 门禁 2/2: PASS${NC}"
        fi

        echo ""
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${RED}✗✗✗ 目标未达成: $(( ($gate1_result == 0 ? 1 : 0) + ($gate2_result == 0 ? 1 : 0) ))/2 PASS ✗✗✗${NC}"
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    fi

    echo "=========================================="

    # 显示详细结果
    if [[ $gate1_result -ne 0 || $gate2_result -ne 0 ]]; then
        show_detailed_results "$task_id"
    fi

    # 生成结果报告
    generate_result_report "$task_id" "$gate1_result" "$gate2_result"

    echo ""
    echo "完成时间: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo ""

    # 返回结果
    if [[ $gate1_result -eq 0 && $gate2_result -eq 0 ]]; then
        exit 0
    else
        exit 1
    fi
}

# 执行主函数
main "$@"
