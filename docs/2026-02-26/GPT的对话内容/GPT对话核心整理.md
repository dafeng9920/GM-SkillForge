# GM-SkillForge L4 战略对话核心整理

> 整理日期：2026-02-26
> 状态：L3 已封板，L4-L6 经济层构建中

---

## 一、核心跃迁逻辑

| 层级 | 核心问题 | 本质 | 定义 |
|------|---------|------|------|
| **L3** | 能不能管？ | 能力治理闭环 | 可阻断、可验真、可版本治理 |
| **L4** | 为什么要让你管？ | 治理经济化闭环 | 治理=可量化收益=经济增值 |
| **L5** | 市场是否被GM分驱动？ | 市场规则绑定 | 排序/认证/分发 |
| **L6** | 收益数据是否真实？ | 运行证据层 | Telemetry、签名、验证 |

### 正确实现顺序（非编号顺序）
```
工程依赖顺序：L6（证据真实性）→ L4（经济计价）→ L5（市场规则）
```

**按编号讲：L4→L5→L6；按落地做：L6→L4→L5**

---

## 二、GM-EVM 收益模型重构

### 2.1 原版问题
四维度（Token/算力/风险/信任）单位不同，直接线性加权会失真：
- E_token 是成本节省比
- E_compute 是资源比例
- R_risk 是概率 × 成本
- C_trust 是品牌溢价

### 2.2 重构方案：统一为 AEV（年度等价美元收益）

```
AEV_total = V_token + V_compute + V_risk + V_trust
GM Premium = α × AEV_total
```

### 2.3 四大收益模块

#### A. Token Efficiency Yield
```python
V_token = (T_orig - T_opt) × P_token × N_calls
```
- 数据来源：Runtime Telemetry
- 校验方式：原始调用日志 + 优化后日志对比

#### B. Compute Lifecycle Yield
```python
V_compute = (InfraCost_baseline - InfraCost_optimized)
```
换算方法：
- 并发密度提升 → 所需实例数减少
- 显存峰值下降 → GPU 型号降级可能
- 折旧周期延长 → 年化成本下降

#### C. Risk Mitigation Value
```python
V_risk = P_incident × ExpectedLoss
```
要求：必须基于历史事故库或行业风险基准，必须提供 evidence_ref

#### D. Trust Premium Yield
```python
V_trust = ΔCTR × AvgRevenue × N_exposure
```
数据来源：Marketplace 转化数据、L5/L4 认证差异统计

---

## 三、L6 证据层关键设计

### 3.1 当前方案缺陷
- **HMAC 只防篡改，不防伪造**
- **GPU UUID 不是"官方节点证明"**
- **NVML 数据可被伪装或重放**

### 3.2 必须补充的四个安全组件

| 组件 | 作用 | 实现方式 |
|------|------|---------|
| **Nonce Challenge** | 防重放 | 服务端下发一次性 nonce（含有效期） |
| **非对称签名** | 防伪造 | 节点私钥签名（Ed25519），公钥在 Registry 可查 |
| **TPM/HSM 绑定** | 密钥保护 | 私钥存 TPM/HSM，不可导出 |
| **节点证书链** | 身份验证 | GM 给每个官方节点签发证书 |

---

## 四、Evidence Packet Spec v1 协议

### 4.1 参与方与密钥

**Master（主服务器）**
- 维护 Master Key Pair：`master_enc_pub`, `master_enc_priv`
- 维护 Node Registry（`node_id` → `node_sig_pub` / cert chain / status）

**Node（黑匣子节点）**
- 每节点持有 Node Signing Key Pair（建议 Ed25519）
- Node 不需要 master 私钥，只需要 `master_enc_pub`

### 4.2 Envelope 结构（JSON）

```json
{
  "schema": "gm.evidence.envelope.v1",
  "header": {
    "packet_id": "EVP_01J2...ULID",
    "node_id": "GM-NODE-0001",
    "skill_id": "skill-general-skill",
    "skill_hash": "sha256:....",
    "session_id": "SES_01J2...ULID",
    "issued_at": "2026-02-25T12:26:30Z",
    "expires_at": "2026-02-25T12:31:30Z",
    "nonce": "N_01J2...ULID",
    "challenge_id": "CH_01J2...ULID",
    "telemetry_window": {
      "start": "2026-02-25T12:26:00Z",
      "end": "2026-02-25T12:26:30Z",
      "sample_rate_hz": 1
    },
    "alg": {
      "keywrap": "RSA-OAEP-256",
      "aead": "AES-256-GCM",
      "sig": "Ed25519",
      "hash": "SHA-256",
      "canon": "JCS"
    }
  },
  "keywrap": {
    "enc_dek": "base64(...)",
    "enc_dek_alg": "RSA-OAEP-256",
    "aead_nonce": "base64(12-bytes)",
    "aad_hash": "sha256:...."
  },
  "ciphertext": {
    "ct": "base64(...)",
    "tag": "base64(16-bytes)"
  },
  "signature": {
    "sig": "base64(ed25519-signature)",
    "signed_fields": ["header", "keywrap", "ciphertext"],
    "signing_hash": "sha256:...."
  },
  "cert": {
    "chain": ["base64(der-or-pem)..."],
    "kid": "node-cert-kid-0001"
  }
}
```

### 4.3 Evidence Body（被加密的正文）

```json
{
  "schema": "gm.evidence.body.v1",
  "metadata": {
    "skill_id": "skill-general-skill",
    "skill_version": "0.1.0",
    "run_id": "RUN_01J2...ULID",
    "node_id": "GM-NODE-0001",
    "gpu": {
      "model": "NVIDIA ...",
      "uuid": "GPU-....",
      "driver_version": "xxx",
      "pci_bus_id": "0000:01:00.0"
    },
    "runtime": {
      "os": "windows|linux",
      "container": "docker|none",
      "agent_build": "gm-node-runtime@<gitsha>"
    }
  },
  "data": [
    {
      "ts": "2026-02-25T12:26:01Z",
      "power_w": 220.1,
      "temp_c": 64,
      "vram_used_mb": 8123.2,
      "gpu_util_pct": 74,
      "mem_util_pct": 51
    }
  ],
  "artifacts": {
    "stdout_tail": "",
    "stderr_tail": "",
    "trace_hash": "sha256:..."
  }
}
```

### 4.4 最小合规测试（协议级验收）

| 测试 | 描述 | 预期结果 |
|------|------|---------|
| T1 | 改动 ciphertext 任一字节 | 验签或 AEAD 失败 |
| T2 | 重放同 packet | 被拒绝（REPLAY_DETECTED） |
| T3 | 篡改 header.skill_id | 验签失败 |
| T4 | 过期 challenge | 被拒绝（CHALLENGE_EXPIRED） |
| T5 | 伪造 node_id 但无对应 pubkey/cert | 被拒绝（NODE_UNTRUSTED） |

---

## 五、病理诊断引擎（GM-Pathology-Analyzer）

### 5.1 核心代码

```python
import json
import numpy as np

class GMPathologyAnalyzer:
    def __init__(self, log_file):
        with open(log_file, 'r') as f:
            self.report = json.load(f)
        self.data = self.report['data']
        self.vram = [d['vram_used_mb'] for d in self.data]
        self.util = [d['gpu_util_pct'] for d in self.data]
        self.power = [d['power_w'] for d in self.data]

    def detect_vram_leak(self, threshold_slope=0.5):
        """
        判定显存泄漏：如果显存占用随时间线性增长，且没有释放迹象。
        """
        x = np.arange(len(self.vram))
        slope, _ = np.polyfit(x, self.vram, 1)

        is_leaking = slope > threshold_slope
        confidence = min(abs(slope) * 10, 100)
        return is_leaking, slope, confidence

    def detect_invalid_idling(self, util_threshold=20, variance_threshold=5):
        """
        判定无效空转：高占用 + 低波动。
        """
        avg_util = np.mean(self.util)
        var_util = np.var(self.util)

        is_idling = avg_util > util_threshold and var_util < variance_threshold
        return is_idling, avg_util, var_util

    def generate_diagnosis(self):
        """生成自动'处刑诊断书'"""
        leak_status, leak_slope, leak_conf = self.detect_vram_leak()
        idle_status, idle_avg, idle_var = self.detect_invalid_idling()

        diagnosis = {
            "skill_id": self.report['metadata']['skill_id'],
            "verdict": "🔥 FAIL" if (leak_status or idle_status) else "🟢 PASS",
            "findings": []
        }

        if leak_status:
            diagnosis["findings"].append({
                "issue": "显存溢出风险 (VRAM Leakage)",
                "evidence": f"斜率 {leak_slope:.2f} MB/s",
                "impact": "长时间运行将导致 Agent 掉线或系统崩溃。"
            })

        if idle_status:
            diagnosis["findings"].append({
                "issue": "逻辑死循环/无效空转 (Invalid Idling)",
                "evidence": f"平均占用 {idle_avg:.1f}% (波动极低: {idle_var:.2f})",
                "impact": "正在吞噬你的算力，但没有产出任何有效结果。"
            })

        if not diagnosis["findings"]:
            diagnosis["findings"].append({"issue": "None", "evidence": "运行曲线符合健康工业标准。"})

        return diagnosis
```

### 5.2 诊断输出标准化

```json
{
  "diagnosis_id": "GM-DIAG-20260225-001",
  "skill_id": "Claude-Finance-Master-v1",
  "verdict": "PASS | WARN | FAIL",
  "health_score": 82.4,
  "risk_level": "LOW | MEDIUM | HIGH",
  "metrics": {
    "vram_slope_mb_per_sec": 0.32,
    "vram_peak_mb": 8123,
    "utilization_avg_pct": 74.1,
    "utilization_variance": 38.2,
    "power_avg_w": 221.4,
    "util_power_correlation": 0.88
  },
  "flags": [
    {
      "issue": "VRAM Growth Trend",
      "severity": "MEDIUM",
      "score": 0.63
    }
  ],
  "estimated_impact_usd_monthly": 18.40,
  "generated_at": "2026-02-25T12:30:00Z"
}
```

### 5.3 升级要求

| 原方法 | 问题 | 升级方案 |
|--------|------|---------|
| `detect_vram_leak` 单纯线性斜率 | warm-up 会误判 | 分段回归 + 最大回撤 + 平台判定 |
| `detect_invalid_idling` 仅用 util 均值+方差 | 稳定算子误伤 | 加入 `corr(util, power)` + 频域能量分析 |
| `confidence = min(abs(slope)*10,100)` | 拍脑袋 | bootstrap 重采样估计置信区间 |

---

## 六、硬件指纹记录器（GMSecureLogger）

```python
import pynvml
import time
import json
import hashlib
import hmac
from datetime import datetime

class GMSecureLogger:
    def __init__(self, secret_key="GM_CORE_SECRET"):
        pynvml.nvmlInit()
        self.handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        self.secret_key = secret_key.encode()
        self.device_name = pynvml.nvmlDeviceGetName(self.handle)
        self.gpu_uuid = pynvml.nvmlDeviceGetUUID(self.handle)

    def get_hardware_snapshot(self):
        """抓取瞬时物理数据"""
        power = pynvml.nvmlDeviceGetPowerUsage(self.handle) / 1000.0
        temp = pynvml.nvmlDeviceGetTemperature(self.handle, pynvml.NVML_TEMPERATURE_GPU)
        mem = pynvml.nvmlDeviceGetMemoryInfo(self.handle)
        util = pynvml.nvmlDeviceGetUtilizationRates(self.handle)

        return {
            "ts": datetime.now().isoformat(),
            "power_w": power,
            "temp_c": temp,
            "vram_used_mb": mem.used / 1024**2,
            "gpu_util_pct": util.gpu,
            "mem_util_pct": util.memory
        }

    def generate_secure_log(self, skill_id, duration_sec=5):
        """生成带硬件指纹的加密审计日志"""
        telemetry_data = []
        for _ in range(duration_sec):
            telemetry_data.append(self.get_hardware_snapshot())
            time.sleep(1)

        payload = {
            "metadata": {
                "skill_id": skill_id,
                "gpu_model": self.device_name,
                "gpu_uuid": self.gpu_uuid,
                "audit_engine": "GM-SkillForge-L6"
            },
            "data": telemetry_data
        }

        data_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(self.secret_key, data_str.encode(), hashlib.sha256).hexdigest()
        payload["gm_signature"] = signature

        log_filename = f"evidence_{skill_id}_{int(time.time())}.gm.json"
        with open(log_filename, "w") as f:
            json.dump(payload, f, indent=4)

        return log_filename
```

---

## 七、主服务器数据吞噬接口（GM-Master-Ingest）

```python
from fastapi import FastAPI, Request, HTTPException
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import json

app = FastAPI()

# 加载主服务器私钥
with open("master_ops.key", "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(), password=None
    )

def calculate_evm_revenue(pathology_data):
    """GM-EVM 核心计价逻辑：将病理特征转化为美金"""
    TOKEN_PRICE = 0.00001
    HARDWARE_COST_PER_HOUR = 0.85

    avg_power = sum(d['power_w'] for d in pathology_data) / len(pathology_data)

    v_token_savings = 1200.0
    v_compute_savings = avg_power * 0.4 * 24 * 365 / 1000 * 0.12

    return v_token_savings + v_compute_savings

@app.post("/v1/telemetry/ingest")
async def ingest_evidence(request: Request):
    encrypted_payload = await request.body()
    node_id = request.headers.get("X-GM-Node-ID")
    skill_id = request.headers.get("X-GM-Skill-Hash")

    try:
        decrypted_data = private_key.decrypt(
            encrypted_payload,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        evidence_json = json.loads(decrypted_data)
        pathology_data = evidence_json.get("data")

        estimated_annual_savings = calculate_evm_revenue(pathology_data)

        return {
            "status": "INGESTED",
            "receipt_hash": hash(decrypted_data),
            "aev_projected": estimated_annual_savings
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail="DECRYPTION_FAILED_OR_INVALID_DATA")
```

### 工程修正点
1. **不能用 RSA-OAEP 直接解密整包** → 混合加密（AES-GCM + RSA-OAEP）
2. **缺"谁发来的"证明** → 节点私钥签名 + nonce challenge + node registry
3. **receipt_hash 不能用 Python hash()** → 用 SHA256(canonical_payload)

---

## 八、Success-First Autonomous Router v1

### 8.1 设计目标

**硬约束（必须满足）**
- 任务必须产出：`RESULT | PARTIAL_RESULT | NEEDS_INPUT | STOPPED_SAFE`
- 不允许无穷递归与无效空转
- 失败必须可解释、可复现（有 trace）

**优化目标（在硬约束内）**
- Token/调用次数/外部请求/耗时/算力最小化

### 8.2 核心对象

#### Task Context（输入）
```json
{
  "task_id": "T_...",
  "user_goal": "string",
  "constraints": {
    "time_budget_sec": 60,
    "cost_budget_units": 10,
    "risk_tolerance": "low|medium|high",
    "success_priority": "high"
  },
  "artifacts": {
    "files": [],
    "urls": [],
    "history_summary": "string"
  }
}
```

#### Skill Descriptor（每个 Skill 必须提供的元信息）
```json
{
  "skill_id": "skill.xxx",
  "fingerprint": {
    "intent": ["summarize", "extract", "refactor", "trade-analyze"],
    "keywords": ["risk", "alert", "profit", "audit"],
    "required_inputs": ["text|file|url|json"],
    "negative_triggers": ["medical", "legal-advice-highstakes"]
  },
  "io_contract": {
    "input_schema": "jsonschema://...",
    "output_schema": "jsonschema://...",
    "must_return": ["status", "result|next_questions|error"]
  },
  "cost_profile": {
    "tier": "low|medium|high",
    "est_tokens": 800,
    "est_latency_ms": 1500,
    "external_calls": ["optional|required"],
    "fallback_available": true
  },
  "reliability": {
    "expected_success_rate": 0.85,
    "known_failure_modes": ["format_drift", "missing_context"]
  }
}
```

### 8.3 两阶段路由策略

#### Phase A：Success Guard（默认）
**触发条件：**
- depth == 0（首次）
- 路由置信度 < 0.7
- 用户显式"必须成功"

**策略：**
- 优先选成功率高的 Skill
- 允许中高成本，但必须受预算硬约束
- 不轻易熔断；先尝试修复与补全

#### Phase B：Cost Optimizer（省钱模式）
**触发条件：**
- 预算进入低水位（remaining <= 30%）
- 或路由置信度 >= 0.8 且已有可用结果
- 或任务重复模式稳定（可缓存/复用）

**策略：**
- 优先 low-tier Skill / 摘要 / 采样
- 更强门控、更强缓存
- 更早 PAUSE_FOR_CONFIRM（预算临界）

### 8.4 选择算法

```
S = 0.55*Success + 0.25*Relevance + 0.15*BudgetFit + 0.05*CostEfficiency

Phase A：Success 权重最大
Phase B：CostEfficiency 权重上调，Success 仍是底线
```

### 8.5 降级梯度（Fallback Ladder）

| 顺序 | 降级方式 | 描述 |
|------|---------|------|
| 1 | FORMAT_FIX | 只修输出格式，不重做推理 |
| 2 | ASK_MIN_QUESTIONS | 问 1–3 个最小澄清问题 |
| 3 | PARTIAL_RESULT | 给 70–90% 方案 + 风险点 |
| 4 | STOPPED_SAFE | 安全停止 + 下一步建议 |

---

## 九、ROUTER_POLICY.md（给人看）

```markdown
# ROUTER_POLICY.md — Success-First Autonomous Router v1

## 1) 三条铁律

### 1.1 Cost-Check（代价感知）
- 若上下文过大，优先做"摘要/采样"，不要一上来全量推理。
- 默认目标：单次任务 Token 消耗压制在阈值以内。
- 若预测本次动作成本超过阈值，必须暂停并请求确认。

### 1.2 Anti-Loop（防循环熔断）
- 任何任务都必须有递归深度上限（depth_limit）。
- 若连续 N 轮无"实质进展"，自动熔断，输出安全停止。
- 不允许"无限重试"与"无效空转"。

### 1.3 Precision-Gating（精度门控）
- 只有在意图匹配且置信度达标时才启用重型/高成本路径。
- 置信度不足时走低成本路径。
- 门控必须配套降级梯度，防止"呆板不动"。

## 2) 核心输出状态
- RESULT：完成，给出最终结果
- PARTIAL_RESULT：给出可用的 70–90% 方案
- NEEDS_INPUT：必须补充 1–3 个最小信息
- PAUSE_FOR_CONFIRM：等待用户确认
- STOPPED_SAFE：安全停止并说明原因

## 3) 默认参数
| 参数 | 默认值 | 说明 |
|---|---:|---|
| context_length_threshold_bytes | 12288 | >12KB 先摘要/采样 |
| token_target_per_task | 1500 | 单任务目标 token 上限 |
| depth_limit | 3 | 最大递归深度 |
| no_progress_turn_limit | 3 | 连续无进展轮数阈值 |
| gating_confidence_threshold | 0.85 | 深度处理门槛 |
| pause_cost_usd_threshold | 0.10 | 预计成本>阈值→暂停确认 |
| budget_units_total | 10 | 单任务预算单位 |
```

---

## 十、router_policy.schema.json（给机器用）

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "gm.router_policy.schema.v1",
  "title": "Success-First Autonomous Router Policy v1",
  "type": "object",
  "required": ["schema", "version", "principles", "defaults", "states", "routing", "progress_signal", "anti_loop", "fallback", "budget", "audit"],
  "properties": {
    "schema": { "type": "string", "const": "gm.router_policy.v1" },
    "version": { "type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$" },
    "principles": {
      "type": "object",
      "required": ["cost_check", "anti_loop", "precision_gating"],
      "properties": {
        "cost_check": {
          "type": "object",
          "required": ["context_length_threshold_bytes", "token_target_per_task", "pause_cost_usd_threshold"],
          "properties": {
            "context_length_threshold_bytes": { "type": "integer", "minimum": 1024 },
            "token_target_per_task": { "type": "integer", "minimum": 100 },
            "pause_cost_usd_threshold": { "type": "number", "minimum": 0 }
          }
        },
        "anti_loop": {
          "type": "object",
          "required": ["depth_limit", "no_progress_turn_limit"],
          "properties": {
            "depth_limit": { "type": "integer", "minimum": 1, "maximum": 10 },
            "no_progress_turn_limit": { "type": "integer", "minimum": 1, "maximum": 10 }
          }
        },
        "precision_gating": {
          "type": "object",
          "required": ["confidence_threshold"],
          "properties": {
            "confidence_threshold": { "type": "number", "minimum": 0, "maximum": 1 }
          }
        }
      }
    }
  }
}
```

---

## 十一、默认 policy.json

```json
{
  "schema": "gm.router_policy.v1",
  "version": "1.0.0",
  "principles": {
    "cost_check": {
      "context_length_threshold_bytes": 12288,
      "token_target_per_task": 1500,
      "pause_cost_usd_threshold": 0.1,
      "large_context_preprocess": "SUMMARY_EXTRACTION"
    },
    "anti_loop": {
      "depth_limit": 3,
      "no_progress_turn_limit": 3,
      "loop_patterns": ["ABA_BOUNCE", "REPEAT_SAME_SKILL", "NO_PROGRESS"]
    },
    "precision_gating": {
      "confidence_threshold": 0.85,
      "activation_keywords": ["audit", "evidence", "diagnosis", "pathology", "evm", "risk", "optimize", "refactor"],
      "low_confidence_behavior": ["ASK_MIN_QUESTIONS", "CALL_LOW_COST_SKILL", "GUIDE"]
    }
  },
  "defaults": {
    "budget_units_total": 10,
    "budget_low_watermark_ratio": 0.3,
    "budget_critical_ratio": 0.1
  },
  "states": {
    "allowed_final_states": ["RESULT", "PARTIAL_RESULT", "NEEDS_INPUT", "PAUSE_FOR_CONFIRM", "STOPPED_SAFE"]
  },
  "routing": {
    "phases": [
      {
        "phase_id": "SUCCESS_GUARD",
        "name": "Success Guard (default)",
        "weights": { "success": 0.55, "relevance": 0.25, "budget_fit": 0.15, "cost_efficiency": 0.05 }
      },
      {
        "phase_id": "COST_OPTIMIZER",
        "name": "Cost Optimizer",
        "weights": { "success": 0.45, "relevance": 0.25, "budget_fit": 0.15, "cost_efficiency": 0.15 }
      }
    ]
  },
  "fallback": {
    "sequence": ["FORMAT_FIX", "ASK_MIN_QUESTIONS", "PARTIAL_RESULT", "STOPPED_SAFE"],
    "max_retries": 1
  },
  "budget": {
    "unit_costs": { "low_skill_call": 1, "medium_skill_call": 3, "high_skill_call": 6, "external_call": 2, "rerun": 1 }
  }
}
```

---

## 十二、Skill + n8n 集成架构

### 12.1 总体架构
```
UI → SkillForge → Router/Compiler → n8n → Result/Evidence → Report
```

### 12.2 TaskSpec（可编译 Skill 结构）

```json
{
  "task_id": "T_01",
  "goal": "每天抓取指定关键词的推特/新闻，生成摘要并推送到 Telegram",
  "constraints": {
    "max_cost_usd": 0.2,
    "deadline_sec": 120,
    "risk_tolerance": "low"
  },
  "inputs": {
    "keywords": ["btc", "eth"],
    "telegram_chat_id": "..."
  },
  "steps": [
    {"id":"s1","op":"HTTP_FETCH","args":{"url":"...","method":"GET"}},
    {"id":"s2","op":"PARSE","args":{"type":"jsonpath","expr":"..."}},
    {"id":"s3","op":"LLM_SUMMARIZE","args":{"max_tokens":400}},
    {"id":"s4","op":"TELEGRAM_SEND","args":{"chat_id":"...","text_from":"s3"}}
  ],
  "outputs": {
    "deliverable": "telegram_message",
    "artifacts": ["summary_md", "run_log"]
  }
}
```

### 12.3 n8n 适配映射

| TaskSpec op | n8n 节点 |
|-------------|---------|
| HTTP_FETCH | HTTP Request node |
| PARSE | Function / Code node（JS） |
| LLM_SUMMARIZE | OpenAI/Gemini node |
| TELEGRAM_SEND | Telegram node |

---

## 十三、Marketplace 护城河逻辑

### 13.1 壁垒来源（非算法）
- Runtime Telemetry 数据池
- Risk Benchmark Library
- Marketplace CTR 数据
- 连续版本演化记录

### 13.2 护城河条件
- GM 分绑定排序
- 认证绑定转化
- 收益报告强制展示
- 数据不可导出

### 13.3 真正的护城河应放在哪里？

```
护城河 = 执行证据 + 风险模型 + 成本计价数据库
```

不是：
- Prompt 模板
- Routing 算法
- 生成能力

---

## 十四、与 OpenClaw 的竞争差异

### 14.1 差异定位

| 维度 | OpenClaw | GM-SkillForge |
|------|----------|---------------|
| 定位 | 聪明的执行者 | 冷静的调度与治理者 |
| 优势 | 快速生成、自然语言直出、低门槛 | 可控性、可解释性、可量化 |
| 目标用户 | 玩自动化的人 | 已被自动化伤过的人 |

### 14.2 三张可打的牌

| 牌 | OpenClaw | GM-SkillForge |
|----|----------|---------------|
| 失败可解释 | "任务失败" | "任务在步骤 3 因 HTTP 500 失败，已重试 1 次..." |
| 成本上限 | 默认无限尝试 | 预算 10 单位，用完即停 |
| 熔断机制 | 可能无限重试 | 检测到 A→B→A 循环，已停止 |

---

## 十五、单人推进策略

### 15.1 轻量闭环引擎（推荐）

**只做：**
1. Node Recorder（生成证据，Ed25519 签名）
2. Ingest Service（验签、解密、写入数据库）
3. Pathology Analyzer（计算关键风险指标）
4. EVM Engine（统一美元化计价）
5. Report Generator（输出 Markdown / JSON 报告）

**不做：**
- 市场层
- 全球节点
- 复杂证书链
- UI 平台

### 15.2 升级路径

```
阶段 1（完成闭环）
→ 阶段 2（节点身份体系）
→ 阶段 3（在线 challenge 防重放）
→ 阶段 4（多节点注册）
→ 阶段 5（市场绑定）
```

---

## 十六、关键认知总结

### 核心跃迁
> **L3 是工程闭环，L4 是经济闭环，L6 是证据抓手**

### 战略定位
> **当 GM 分成为安装前必看指标时，你就不再是工具，而是治理层**

### 护城河本质
> **护城河来自数据，而非算法**

### 产品级别
> **做到严格审计协议级后，产品级别从"优化工具"跃迁为"可信运行与收益结算网络"**

### 单人原则
> **单人做基础设施，必须做一个可以自洽的小宇宙，而不是统治世界的蓝图**

---

## 十七、今晚任务建议

1. 写出 L6 升级清单
2. 把 TODO 分类放入 A/B/C 三类
3. 只做定标，不做实现

### TODO 分类

**A 类（必须存在否则系统断裂）**
- 审计日志修正
- 测试覆盖
- Pipeline 稳定性
- 回归脚本固化

**B 类（优化型）**
- 模板美化
- 输出改进
- 提示词增强
- 文档补充

**C 类（诱惑型 - 全部延后）**
- Marketplace 架构
- 认证体系
- GM Premium 抽成
- 评分展示
- 对外叙事包装
