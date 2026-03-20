"""
Discovery Pipeline - T1-T6 总装实现

本模块实现第 1 批完整发现链：
intake -> parse -> validate -> scan -> pattern -> findings

硬约束：
- 不得引入第 2 批和第 3 批能力
- 不得依赖人工拼接流程
- 任一步骤失败必须 fail-closed
- 无 EvidenceRef 不得宣称完成

流水线输出目录结构 (固定)：
run/<run_id>/
├── intake_request.json       # T1 产出
├── normalized_skill_spec.json # T2 产出
├── validation_report.json     # T3 产出
├── rule_scan_report.json      # T4 产出
├── pattern_detection_report.json # T5 产出
└── findings.json              # T6 产出

@contact: 执行者 Kior-C
@task_id: T7
@date: 2026-03-15
"""

from __future__ import annotations

import json
import hashlib
import logging
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, List, Dict, Literal
import traceback

# 导入 T1-T6 模块
try:
    from skillforge.src.contracts.intake_request import (
        IntakeRequest,
        create_intake_request,
        validate_intake_request,
    )
    from skillforge.src.contracts.skill_spec import (
        SkillParser,
        ParseResult,
        NormalizedSkillSpec,
    )
    from skillforge.src.contracts.skill_contract_validator import (
        SkillContractValidator,
        ValidationResult,
    )
    from skillforge.src.contracts.rule_scanner import (
        RuleScanner,
        RuleScanResult,
    )
    from skillforge.src.contracts.pattern_matcher import (
        PatternMatcher,
        PatternMatchResult,
    )
    from skillforge.src.contracts.finding_builder import (
        FindingBuilder,
        FindingsReport,
        FindingsReportBuilder,
    )
except ImportError as e:
    # 处理直接运行时的导入问题
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    try:
        from contracts.intake_request import (
            IntakeRequest,
            create_intake_request,
            validate_intake_request,
        )
        from contracts.skill_spec import (
            SkillParser,
            ParseResult,
            NormalizedSkillSpec,
        )
        from contracts.skill_contract_validator import (
            SkillContractValidator,
            ValidationResult,
        )
        from contracts.rule_scanner import (
            RuleScanner,
            RuleScanResult,
        )
        from contracts.pattern_matcher import (
            PatternMatcher,
            PatternMatchResult,
        )
        from contracts.finding_builder import (
            FindingBuilder,
            FindingsReport,
            FindingsReportBuilder,
        )
    except ImportError as e2:
        raise ImportError(
            f"无法导入 T1-T6 模块: {e}\n"
            f"重试后: {e2}\n"
            f"请确保 skillforge/src 在 PYTHONPATH 中"
        )


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# 数据结构
# =============================================================================

@dataclass
class PipelineStep:
    """流水线步骤状态"""
    step_name: str
    status: Literal["pending", "running", "completed", "failed"]
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    output_path: Optional[str] = None


@dataclass
class PipelineResult:
    """流水线执行结果"""
    run_id: str
    status: Literal["success", "failed", "partial"]
    started_at: str
    completed_at: str
    steps: List[PipelineStep] = field(default_factory=list)
    total_findings: int = 0
    output_dir: str = ""
    error_summary: List[str] = field(default_factory=list)


# =============================================================================
# 发现流水线
# =============================================================================

class DiscoveryPipeline:
    """
    第 1 批发现链流水线

    流程：intake -> parse -> validate -> scan -> pattern -> findings
    """

    def __init__(
        self,
        output_base_dir: str = "run",
        fail_fast: bool = True,  # 任一步骤失败立即停止 (Fail-Closed)
    ):
        """
        初始化流水线

        Args:
            output_base_dir: 输出目录基础路径
            fail_fast: 是否在任一步骤失败时立即停止 (默认 True，硬约束)
        """
        self.output_base_dir = Path(output_base_dir)
        self.fail_fast = fail_fast

        # 初始化各步骤处理器
        self.skill_parser = SkillParser()
        self.contract_validator = SkillContractValidator()
        self.rule_scanner = RuleScanner()
        self.pattern_matcher = PatternMatcher()
        self.finding_builder = FindingBuilder()
        self.findings_report_builder = FindingsReportBuilder()

        # 运行时状态
        self.current_run_dir: Optional[Path] = None
        self.steps: List[PipelineStep] = []

    def run(
        self,
        intent_id: str,
        repo_url: str,
        commit_sha: str,
        skill_dir: str,
        at_time: Optional[str] = None,
        issue_key: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> PipelineResult:
        """
        运行完整发现链

        Args:
            intent_id: 审计意图 ID (T1 白名单)
            repo_url: 仓库 URL
            commit_sha: 提交 SHA (7-40 字符十六进制)
            skill_dir: skill 目录路径 (用于 T2 解析)
            at_time: 审计时间 (ISO-8601)
            issue_key: 问题单号 (可选)
            run_id: 运行 ID (可选，自动生成)

        Returns:
            PipelineResult: 流水线执行结果
        """
        # 生成 run_id
        if run_id is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            hash_input = f"{intent_id}:{commit_sha}:{timestamp}"
            run_id_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:12]
            run_id = f"{timestamp}_{run_id_hash}"

        # 创建运行目录
        self.current_run_dir = self.output_base_dir / run_id
        self.current_run_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"开始流水线运行: run_id={run_id}")
        logger.info(f"输出目录: {self.current_run_dir}")

        started_at = datetime.now(timezone.utc).isoformat()
        steps: List[PipelineStep] = []
        error_summary: List[str] = []

        # Step 1: Intake (T1)
        intake_step = self._step_intake(
            intent_id=intent_id,
            repo_url=repo_url,
            commit_sha=commit_sha,
            at_time=at_time,
            issue_key=issue_key,
        )
        steps.append(intake_step)

        if intake_step.status == "failed":
            return PipelineResult(
                run_id=run_id,
                status="failed",
                started_at=started_at,
                completed_at=datetime.now(timezone.utc).isoformat(),
                steps=steps,
                output_dir=str(self.current_run_dir),
                error_summary=[intake_step.error or "Unknown intake error"],
            )

        # Step 2: Parse (T2)
        parse_step = self._step_parse(skill_dir=skill_dir)
        steps.append(parse_step)

        if parse_step.status == "failed" and self.fail_fast:
            return PipelineResult(
                run_id=run_id,
                status="failed",
                started_at=started_at,
                completed_at=datetime.now(timezone.utc).isoformat(),
                steps=steps,
                output_dir=str(self.current_run_dir),
                error_summary=[parse_step.error or "Unknown parse error"],
            )

        # Step 3: Validate (T3)
        validate_step = self._step_validate()
        steps.append(validate_step)

        if validate_step.status == "failed" and self.fail_fast:
            return PipelineResult(
                run_id=run_id,
                status="failed",
                started_at=started_at,
                completed_at=datetime.now(timezone.utc).isoformat(),
                steps=steps,
                output_dir=str(self.current_run_dir),
                error_summary=[validate_step.error or "Unknown validation error"],
            )

        # Step 4: Scan (T4)
        scan_step = self._step_scan(skill_dir=skill_dir)
        steps.append(scan_step)

        if scan_step.status == "failed" and self.fail_fast:
            return PipelineResult(
                run_id=run_id,
                status="failed",
                started_at=started_at,
                completed_at=datetime.now(timezone.utc).isoformat(),
                steps=steps,
                output_dir=str(self.current_run_dir),
                error_summary=[scan_step.error or "Unknown scan error"],
            )

        # Step 5: Pattern (T5)
        pattern_step = self._step_pattern(skill_dir=skill_dir)
        steps.append(pattern_step)

        if pattern_step.status == "failed" and self.fail_fast:
            return PipelineResult(
                run_id=run_id,
                status="failed",
                started_at=started_at,
                completed_at=datetime.now(timezone.utc).isoformat(),
                steps=steps,
                output_dir=str(self.current_run_dir),
                error_summary=[pattern_step.error or "Unknown pattern detection error"],
            )

        # Step 6: Findings (T6)
        findings_step = self._step_findings()
        steps.append(findings_step)

        # Fail-Closed: T6 失败时立即停止
        if findings_step.status == "failed" and self.fail_fast:
            return PipelineResult(
                run_id=run_id,
                status="failed",
                started_at=started_at,
                completed_at=datetime.now(timezone.utc).isoformat(),
                steps=steps,
                output_dir=str(self.current_run_dir),
                error_summary=[findings_step.error or "Unknown findings error"],
            )

        completed_at = datetime.now(timezone.utc).isoformat()

        # 计算总 findings 数量
        total_findings = 0
        if findings_step.status == "completed" and findings_step.output_path:
            try:
                with open(findings_step.output_path, "r", encoding="utf-8") as f:
                    findings_report = json.load(f)
                    total_findings = findings_report.get("summary", {}).get("total_findings", 0)
            except Exception as e:
                logger.warning(f"无法读取 findings.json: {e}")

        # 判断整体状态
        failed_steps = [s for s in steps if s.status == "failed"]
        if failed_steps:
            status = "failed" if self.fail_fast else "partial"
            error_summary = [s.error or f"{s.step_name} failed" for s in failed_steps]
        else:
            status = "success"

        return PipelineResult(
            run_id=run_id,
            status=status,
            started_at=started_at,
            completed_at=completed_at,
            steps=steps,
            total_findings=total_findings,
            output_dir=str(self.current_run_dir),
            error_summary=error_summary,
        )

    def _step_intake(
        self,
        intent_id: str,
        repo_url: str,
        commit_sha: str,
        at_time: Optional[str],
        issue_key: Optional[str],
    ) -> PipelineStep:
        """Step 1: Intake (T1)"""
        step = PipelineStep(
            step_name="T1_Intake",
            status="running",
            started_at=datetime.now(timezone.utc).isoformat(),
        )
        logger.info(f"[T1] 开始 Intake: intent_id={intent_id}, repo_url={repo_url}")

        try:
            # 创建 IntakeRequest (T1 新接口)
            intake_request = create_intake_request(
                intent_id=intent_id,
                repo_url=repo_url,
                commit_sha=commit_sha,
                at_time=at_time,
                issue_key=issue_key,
            )

            # 验证 (T1 强制要求) - 需要传入字典
            request_dict = {
                "intent_id": intake_request.intent_id,
                "repo_url": intake_request.repo_url,
                "commit_sha": intake_request.commit_sha,
                "at_time": intake_request.at_time,
                "issue_key": intake_request.issue_key,
            }
            validation = validate_intake_request(request_dict)
            if not validation.valid:
                step.status = "failed"
                error_msg = validation.errors[0] if validation.errors else "Unknown validation error"
                step.error = f"Intake validation failed: {error_msg}"
                step.completed_at = datetime.now(timezone.utc).isoformat()
                logger.error(f"[T1] {step.error}")
                return step

            # 保存 intake_request.json
            output_path = self.current_run_dir / "intake_request.json"
            intake_request.save(str(output_path))

            step.status = "completed"
            step.output_path = str(output_path)
            step.completed_at = datetime.now(timezone.utc).isoformat()
            logger.info(f"[T1] 完成: {output_path}")

        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            step.completed_at = datetime.now(timezone.utc).isoformat()
            logger.error(f"[T1] 错误: {e}\n{traceback.format_exc()}")

        return step

    def _step_parse(self, skill_dir: str) -> PipelineStep:
        """Step 2: Parse (T2)"""
        step = PipelineStep(
            step_name="T2_Parse",
            status="running",
            started_at=datetime.now(timezone.utc).isoformat(),
        )
        logger.info(f"[T2] 开始 Parse: skill_dir={skill_dir}")

        try:
            # 解析 skill 目录 (使用 parse_skill 方法)
            result: ParseResult = self.skill_parser.parse_skill(skill_dir)

            if not result.is_valid:
                step.status = "failed"
                error_msgs = [e.message for e in result.errors]
                step.error = f"Skill parsing failed: {', '.join(error_msgs)}"
                step.completed_at = datetime.now(timezone.utc).isoformat()
                logger.error(f"[T2] {step.error}")
                return step

            # 保存 normalized_skill_spec.json
            output_path = self.current_run_dir / "normalized_skill_spec.json"
            result.spec.save(str(output_path))

            step.status = "completed"
            step.output_path = str(output_path)
            step.completed_at = datetime.now(timezone.utc).isoformat()
            logger.info(f"[T2] 完成: {output_path}")

        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            step.completed_at = datetime.now(timezone.utc).isoformat()
            logger.error(f"[T2] 错误: {e}\n{traceback.format_exc()}")

        return step

    def _step_validate(self) -> PipelineStep:
        """Step 3: Validate (T3)"""
        step = PipelineStep(
            step_name="T3_Validate",
            status="running",
            started_at=datetime.now(timezone.utc).isoformat(),
        )
        logger.info("[T3] 开始 Validate")

        try:
            # 读取 normalized_skill_spec.json
            spec_path = self.current_run_dir / "normalized_skill_spec.json"
            if not spec_path.exists():
                step.status = "failed"
                step.error = "normalized_skill_spec.json not found"
                step.completed_at = datetime.now(timezone.utc).isoformat()
                logger.error(f"[T3] {step.error}")
                return step

            with open(spec_path, "r", encoding="utf-8") as f:
                spec_data = json.load(f)

            # 执行合同校验
            result: ValidationResult = self.contract_validator.validate_skill_spec(spec_data)

            # 保存 validation_report.json
            output_path = self.current_run_dir / "validation_report.json"
            report_dict = {
                "is_valid": result.is_valid,
                "failures": [asdict(f) for f in result.failures],
                "warnings": [asdict(w) for w in result.warnings],
                "validated_at": result.validated_at,
                "validator_version": result.validator_version,
                "failure_count": len(result.failures),
                "warning_count": len(result.warnings),
            }
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(report_dict, f, indent=2, ensure_ascii=False)

            if not result.is_valid:
                step.status = "failed"
                error_msgs = [f"{f.code}: {f.message}" for f in result.failures]
                step.error = f"Validation failed: {', '.join(error_msgs)}"
                step.completed_at = datetime.now(timezone.utc).isoformat()
                logger.error(f"[T3] {step.error}")
                return step

            step.status = "completed"
            step.output_path = str(output_path)
            step.completed_at = datetime.now(timezone.utc).isoformat()
            logger.info(f"[T3] 完成: {output_path}")

        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            step.completed_at = datetime.now(timezone.utc).isoformat()
            logger.error(f"[T3] 错误: {e}\n{traceback.format_exc()}")

        return step

    def _step_scan(self, skill_dir: str) -> PipelineStep:
        """Step 4: Scan (T4)"""
        step = PipelineStep(
            step_name="T4_Scan",
            status="running",
            started_at=datetime.now(timezone.utc).isoformat(),
        )
        logger.info(f"[T4] 开始 Scan: skill_dir={skill_dir}")

        try:
            # 执行规则扫描 (使用 scan_skill 方法)
            result: RuleScanResult = self.rule_scanner.scan_skill(skill_dir)

            # 保存 rule_scan_report.json
            output_path = self.current_run_dir / "rule_scan_report.json"
            result.save(str(output_path))

            step.status = "completed"
            step.output_path = str(output_path)
            step.completed_at = datetime.now(timezone.utc).isoformat()
            logger.info(f"[T4] 完成: {output_path}, hits={result.total_hits}")

        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            step.completed_at = datetime.now(timezone.utc).isoformat()
            logger.error(f"[T4] 错误: {e}\n{traceback.format_exc()}")

        return step

    def _step_pattern(self, skill_dir: str) -> PipelineStep:
        """Step 5: Pattern (T5)"""
        step = PipelineStep(
            step_name="T5_Pattern",
            status="running",
            started_at=datetime.now(timezone.utc).isoformat(),
        )
        logger.info(f"[T5] 开始 Pattern: skill_dir={skill_dir}")

        try:
            # 执行模式检测 (使用 match_patterns 方法)
            result = self.pattern_matcher.match_patterns(skill_dir)

            # 保存 pattern_detection_report.json
            output_path = self.current_run_dir / "pattern_detection_report.json"
            result.save(str(output_path))

            step.status = "completed"
            step.output_path = str(output_path)
            step.completed_at = datetime.now(timezone.utc).isoformat()
            logger.info(f"[T5] 完成: {output_path}, matches={result.total_matches}")

        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            step.completed_at = datetime.now(timezone.utc).isoformat()
            logger.error(f"[T5] 错误: {e}\n{traceback.format_exc()}")

        return step

    def _step_findings(self) -> PipelineStep:
        """Step 6: Findings (T6)"""
        step = PipelineStep(
            step_name="T6_Findings",
            status="running",
            started_at=datetime.now(timezone.utc).isoformat(),
        )
        logger.info("[T6] 开始 Findings")

        try:
            # 读取 skill spec 获取 skill_id 和 skill_name
            spec_path = self.current_run_dir / "normalized_skill_spec.json"
            if not spec_path.exists():
                step.status = "failed"
                step.error = "normalized_skill_spec.json not found"
                step.completed_at = datetime.now(timezone.utc).isoformat()
                logger.error(f"[T6] {step.error}")
                return step

            with open(spec_path, "r", encoding="utf-8") as f:
                spec_data = json.load(f)
            skill_id = spec_data.get("skill_id", "unknown")
            skill_name = spec_data.get("skill_name", "unknown")

            # 读取各步骤报告
            validation_path = self.current_run_dir / "validation_report.json"
            scan_path = self.current_run_dir / "rule_scan_report.json"
            pattern_path = self.current_run_dir / "pattern_detection_report.json"

            # 创建带有 get_all_hits 方法的 rule_result 对象
            rule_result = None
            if scan_path.exists():
                with open(scan_path, "r", encoding="utf-8") as f:
                    scan_data = json.load(f)

                # 从 JSON 数据重构带有 get_all_hits 方法的对象
                class RuleResultWrapper:
                    def __init__(self, data):
                        self.data = data
                        self.all_hits = []
                        # 从各个严重级别收集 hits
                        for severity in ['critical_hits', 'high_hits', 'medium_hits', 'low_hits']:
                            for hit in data.get(severity, []):
                                self.all_hits.append(type('RuleHit', (), hit)())

                    def get_all_hits(self):
                        return self.all_hits

                rule_result = RuleResultWrapper(scan_data)

            # 创建带有 get_all_matches 方法的 pattern_result 对象
            pattern_result = None
            if pattern_path.exists():
                with open(pattern_path, "r", encoding="utf-8") as f:
                    pattern_data = json.load(f)

                class PatternResultWrapper:
                    def __init__(self, data):
                        self.data = data
                        self.all_matches = []
                        # 收集 pattern matches - pattern_matches 是字典，包含 critical/high/medium 键
                        pattern_matches = data.get('pattern_matches', {})
                        for severity in ['critical', 'high', 'medium']:
                            for match in pattern_matches.get(severity, []):
                                self.all_matches.append(type('PatternMatch', (), match)())

                    def get_all_matches(self):
                        return self.all_matches

                    @property
                    def governance_gaps(self):
                        # 返回 governance gaps
                        gaps = []
                        for gap in self.data.get('governance_gaps', []):
                            gaps.append(type('GovernanceGap', (), gap)())
                        return gaps

                pattern_result = PatternResultWrapper(pattern_data)

            # 使用 FindingsReportBuilder 构建 findings
            report: FindingsReport = self.findings_report_builder.build_from_reports(
                skill_id=skill_id,
                skill_name=skill_name,
                rule_result=rule_result,
                pattern_result=pattern_result,
                validation_report_path=str(validation_path) if validation_path.exists() else None,
                rule_scan_report_path=str(scan_path) if scan_path.exists() else None,
                pattern_detection_report_path=str(pattern_path) if pattern_path.exists() else None,
            )

            # 保存 findings.json
            output_path = self.current_run_dir / "findings.json"
            report.save(str(output_path))

            step.status = "completed"
            step.output_path = str(output_path)
            step.completed_at = datetime.now(timezone.utc).isoformat()
            logger.info(f"[T6] 完成: {output_path}, findings={len(report.findings)}")

        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            step.completed_at = datetime.now(timezone.utc).isoformat()
            logger.error(f"[T6] 错误: {e}\n{traceback.format_exc()}")

        return step


# =============================================================================
# CLI 接口
# =============================================================================

def run_discovery_pipeline(
    intent_id: str,
    repo_url: str,
    commit_sha: str,
    skill_dir: str,
    output_dir: str = "run",
    at_time: Optional[str] = None,
    issue_key: Optional[str] = None,
) -> PipelineResult:
    """
    运行发现链的便捷函数

    Args:
        intent_id: 审计意图 ID (必须来自 T1 白名单)
        repo_url: 仓库 URL
        commit_sha: 提交 SHA
        skill_dir: skill 目录路径
        output_dir: 输出目录
        at_time: 审计时间
        issue_key: 问题单号

    Returns:
        PipelineResult
    """
    pipeline = DiscoveryPipeline(output_base_dir=output_dir)
    return pipeline.run(
        intent_id=intent_id,
        repo_url=repo_url,
        commit_sha=commit_sha,
        skill_dir=skill_dir,
        at_time=at_time,
        issue_key=issue_key,
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SkillForge 发现链流水线 (T7)")
    parser.add_argument("--intent-id", required=True, help="审计意图 ID (T1 白名单)")
    parser.add_argument("--repo-url", required=True, help="仓库 URL")
    parser.add_argument("--commit-sha", required=True, help="提交 SHA (7-40 字符)")
    parser.add_argument("--skill-dir", required=True, help="skill 目录路径")
    parser.add_argument("--output-dir", default="run", help="输出目录")
    parser.add_argument("--at-time", help="审计时间 (ISO-8601)")
    parser.add_argument("--issue-key", help="问题单号")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    result = run_discovery_pipeline(
        intent_id=args.intent_id,
        repo_url=args.repo_url,
        commit_sha=args.commit_sha,
        skill_dir=args.skill_dir,
        output_dir=args.output_dir,
        at_time=args.at_time,
        issue_key=args.issue_key,
    )

    # 输出结果摘要
    print("\n" + "=" * 60)
    print("流水线执行结果")
    print("=" * 60)
    print(f"Run ID: {result.run_id}")
    print(f"状态: {result.status}")
    print(f"输出目录: {result.output_dir}")
    print(f"总 Findings: {result.total_findings}")
    print("\n步骤详情:")
    for step in result.steps:
        status_icon = "✅" if step.status == "completed" else "❌"
        print(f"  {status_icon} {step.step_name}: {step.status}")
        if step.error:
            print(f"     错误: {step.error}")

    if result.error_summary:
        print("\n错误摘要:")
        for error in result.error_summary:
            print(f"  - {error}")

    sys.exit(0 if result.status == "success" else 1)
