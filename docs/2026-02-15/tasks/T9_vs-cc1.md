# T9 任务书 - vs--cc1

> **任务编号**：T9
> **波次**：Wave 4
> **依赖**：无（可与 T8 并行）
> **预计时长**：15 分钟

## 目标

创建 GitHub Actions CI 配置文件，使 `make ci` 可以在 CI 环境中自动运行。

## 交付物

| 文件 | 类型 | 说明 |
|------|------|------|
| `.github/workflows/ci.yml` | 新建 | GitHub Actions CI 配置 |

## 实现指导

### CI 流程

```yaml
name: GM-SkillForge CI

on:
  push:
    branches: [main]
    paths:
      - 'skillforge-spec-pack/**'
  pull_request:
    branches: [main]
    paths:
      - 'skillforge-spec-pack/**'

jobs:
  contract-tests:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: skillforge-spec-pack

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -e .

      - name: Run contract tests
        run: pytest -q

      - name: Validate all examples
        run: python tools/validate.py --all
```

### 关键要求

1. **工作目录**：CI 的 working-directory 必须是 `skillforge-spec-pack`
2. **Python 版本**：使用 3.11（项目要求 >= 3.9）
3. **两步校验**：
   - `pytest -q` — 契约测试
   - `python tools/validate.py --all` — 示例校验
4. **触发条件**：仅当 `skillforge-spec-pack/` 目录变更时触发
5. **配置文件位置**：`.github/workflows/ci.yml`（注意是项目根目录下）

## 红线（不允许）

- ❌ 不得修改任何 Python 代码或 schema 文件
- ❌ 不得安装项目 `pyproject.toml` 以外的依赖
- ❌ 不得使用 Docker 或其他复杂构建工具
- ❌ 不得添加 secrets 或外部服务调用

## 验收标准

1. `.github/workflows/ci.yml` 是有效 YAML
2. 使用 `actions/checkout@v4` 和 `actions/setup-python@v5`
3. 包含 `pytest -q` 和 `python tools/validate.py --all` 两步
4. 触发条件包含 push 和 pull_request
5. YAML 语法检查通过：

```bash
# 验证 YAML 可解析
python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"
```

## 汇报格式

```
任务编号：T9
执行者：vs--cc1
状态：已完成

改动文件：
- .github/workflows/ci.yml (新建)

验证结果：
[粘贴 YAML 解析结果]

请主控官验收。
```
