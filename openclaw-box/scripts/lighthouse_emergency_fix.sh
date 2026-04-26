#!/bin/bash
# ============================================================
# OpenClaw 2026.x 紧急修复脚本 v2.0
# 适用环境: 腾讯云 Lighthouse 网页终端 (唯一可用输入口)
# 发行日期: 2026-04-03
# 
# 使用方式 (在 Lighthouse 终端粘贴):
#   cat > /root/fix.sh << 'XEOF'
#   <此脚本全部内容>
#   XEOF
#   chmod +x /root/fix.sh && bash /root/fix.sh
# ============================================================
set -euo pipefail

# =================== 🔧 用户必填区 (START) ===================
# ⚠️  请在执行前确认以下 Token 值！
#     Discord Token: 如果已在 Developer Portal 重新生成，请替换下面的值
#     Gateway Token: 用 123456 做紧急恢复，后续可更换为强密码

# ⚠️  Discord Bot Token (已确认)
DISCORD_BOT_TOKEN="YOUR_DISCORD_BOT_TOKEN"
GATEWAY_AUTH_TOKEN="YOUR_GATEWAY_AUTH_TOKEN"
GLM_API_KEY="YOUR_GLM_API_KEY"
OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
OPENAI_API_BASE="https://www.dmxapi.cn/v1"
TAVILY_API_KEY="YOUR_TAVILY_API_KEY"
DISCORD_APP_ID="YOUR_DISCORD_APP_ID"

# =================== 🔧 用户必填区 (END) =====================

OPENCLAW_DIR="/root/openclaw-box"
DATA_DIR="${OPENCLAW_DIR}/data"
CONFIG_FILE="${DATA_DIR}/openclaw.json"
COMPOSE_FILE="${OPENCLAW_DIR}/docker-compose.yml"
ENV_FILE="${OPENCLAW_DIR}/.env"
TS=$(date +%Y%m%dT%H%M%S)

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log_step() { echo -e "\n${CYAN}[$1]${NC} $2"; }
log_ok()   { echo -e "  ${GREEN}✅ $1${NC}"; }
log_warn() { echo -e "  ${YELLOW}⚠️  $1${NC}"; }
log_err()  { echo -e "  ${RED}❌ $1${NC}"; }

echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}  OpenClaw 2026.x 紧急修复脚本 v2.0${NC}"
echo -e "${CYAN}  时间: $(date)${NC}"
echo -e "${CYAN}============================================================${NC}"

# ──────────────────────────────────────────────────────────────
# PRE-CHECK: 确认目录存在
# ──────────────────────────────────────────────────────────────
if [ ! -d "$OPENCLAW_DIR" ]; then
    log_err "未找到 $OPENCLAW_DIR 目录！请确认 OpenClaw 安装路径"
    exit 1
fi

if [ ! -d "$DATA_DIR" ]; then
    log_warn "$DATA_DIR 不存在，创建中..."
    mkdir -p "$DATA_DIR"
fi

# ──────────────────────────────────────────────────────────────
# STEP 1: 全面停机
# ──────────────────────────────────────────────────────────────
log_step "1/8" "⏹  全面停机..."
cd "$OPENCLAW_DIR"

# 尝试多种方式停止
if command -v docker &> /dev/null; then
    docker compose down 2>/dev/null && log_ok "docker compose down 成功" || \
    docker-compose down 2>/dev/null && log_ok "docker-compose down 成功" || {
        docker stop openclaw_core 2>/dev/null || true
        docker stop openclaw_postgres 2>/dev/null || true
        log_ok "容器已直接停止"
    }
else
    log_err "Docker 未安装或不可用!"
    exit 1
fi

# 确认容器已停止
sleep 3
RUNNING=$(docker ps -q --filter "name=openclaw" 2>/dev/null | wc -l)
if [ "$RUNNING" -gt 0 ]; then
    log_warn "仍有 $RUNNING 个容器在运行，强制杀死..."
    docker kill $(docker ps -q --filter "name=openclaw") 2>/dev/null || true
    sleep 2
fi
log_ok "所有容器已停止"

# ──────────────────────────────────────────────────────────────
# STEP 2: 备份当前残局
# ──────────────────────────────────────────────────────────────
log_step "2/8" "💾 备份当前配置..."
BACKUP_DIR="${OPENCLAW_DIR}/backups_${TS}"
mkdir -p "$BACKUP_DIR"

for f in "$CONFIG_FILE" "$COMPOSE_FILE" "$ENV_FILE"; do
    if [ -f "$f" ]; then
        cp "$f" "${BACKUP_DIR}/$(basename $f)"
        echo "  📁 $(basename $f) → backups_${TS}/"
    fi
done
log_ok "备份保存在: $BACKUP_DIR"

# ──────────────────────────────────────────────────────────────
# STEP 3: 重写 .env
# ──────────────────────────────────────────────────────────────
log_step "3/8" "📝 重写 .env 环境变量..."
cat > "$ENV_FILE" << ENVEOF
# ─── OpenClaw 2026.x Environment ───
# Emergency Recovery — Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)

# 1. Main Bot Engine (ZhipuAI / GLM-5)
GLM_API_KEY=${GLM_API_KEY}
GLM_API_BASE=https://open.bigmodel.cn/api/

# 2. Search Radar Expert (DMXAPI / GPT-4o)
OPENAI_API_KEY=${OPENAI_API_KEY}
OPENAI_API_BASE=${OPENAI_API_BASE}
OPENAI_API_MODEL=gpt-4o

# 3. Search Infrastructure
SEARCH_BACKEND=tavily
TAVILY_API_KEY=${TAVILY_API_KEY}
BRAVE_API_KEY=${TAVILY_API_KEY}

# 4. Service Meta
DISCORD_TOKEN=${DISCORD_BOT_TOKEN}
DISCORD_APP_ID=${DISCORD_APP_ID}
OPENCLAW_GATEWAY_TOKEN=${GATEWAY_AUTH_TOKEN}
DATABASE_URL=postgresql://clawuser:clawpassword@openclaw-db:5432/openclaw

# 5. Lark / Feishu (留空待配置)
LARK_APP_ID=
LARK_APP_SECRET=
ENVEOF
log_ok ".env 已重写"

# ──────────────────────────────────────────────────────────────
# STEP 4: 重写 openclaw.json (核心配置)
# 关键修复:
#   - 添加 gateway.auth.mode=token (解决 bind lan 自杀)
#   - 使用 ${ENV_VAR} 引用 (OpenClaw 原生支持)
#   - 保留 plugins.installs 注册信息
# ──────────────────────────────────────────────────────────────
log_step "4/8" "📝 重写 openclaw.json..."

# 注意: 这里用单引号 heredoc 防止 shell 展开 ${...}
# OpenClaw 自身会在运行时解析 ${DISCORD_TOKEN} 等引用
cat > "$CONFIG_FILE" << 'CONFIGEOF'
{
  "meta": {
    "lastTouchedVersion": "2026.3.31",
    "lastTouchedAt": "2026-04-03T12:00:00.000Z"
  },
  "browser": {
    "enabled": true
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "zai/glm-5"
      },
      "compaction": {
        "mode": "safeguard"
      }
    }
  },
  "tools": {
    "web": {
      "search": {
        "enabled": true,
        "provider": "brave"
      },
      "fetch": {
        "enabled": true
      }
    }
  },
  "commands": {
    "native": "auto",
    "nativeSkills": "auto",
    "bash": true,
    "restart": true,
    "ownerDisplay": "raw"
  },
  "channels": {
    "discord": {
      "enabled": true,
      "token": "${DISCORD_TOKEN}",
      "groupPolicy": "open",
      "streaming": "off"
    },
    "openclaw-weixin": {
      "enabled": true
    }
  },
  "gateway": {
    "port": 18793,
    "mode": "local",
    "controlUi": {
      "allowedOrigins": ["*"],
      "dangerouslyAllowHostHeaderOriginFallback": true
    },
    "auth": {
      "mode": "token",
      "token": "${OPENCLAW_GATEWAY_TOKEN}"
    }
  },
  "plugins": {
    "allow": [
      "browser",
      "discord",
      "openclaw-weixin"
    ],
    "entries": {
      "discord": {
        "enabled": true
      },
      "openclaw-weixin": {
        "enabled": true,
        "config": {}
      },
      "brave": {
        "enabled": true,
        "config": {
          "webSearch": {
            "apiKey": "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"
          }
        }
      },
      "browser": {
        "enabled": true
      }
    },
    "installs": {
      "openclaw-weixin": {
        "source": "npm",
        "spec": "@tencent-weixin/openclaw-weixin@compat-host-gte2026.3.0-lt2026.3.22",
        "installPath": "/root/.openclaw/extensions/openclaw-weixin",
        "version": "1.0.3",
        "resolvedName": "@tencent-weixin/openclaw-weixin",
        "resolvedVersion": "1.0.3",
        "resolvedSpec": "@tencent-weixin/openclaw-weixin@1.0.3",
        "integrity": "sha512-TOo9rb5gt3ce3lJEulFT5Ta4/8ocWkR40wzM7lZ8OM3/fjTk3UHYeNjHmDcZlLeg93XYJKdVUFUEiujrf8zMYw==",
        "shasum": "19f65f26d4af26a25f05cdd5f1dd3c687590f91c",
        "resolvedAt": "2026-03-29T17:31:34.482Z",
        "installedAt": "2026-03-29T17:32:04.464Z"
      }
    }
  }
}
CONFIGEOF
log_ok "openclaw.json 已重写 (gateway.auth.mode=token)"

# ──────────────────────────────────────────────────────────────
# STEP 5: 修复 docker-compose.yml 端口映射
# 
# BUG: 原映射 127.0.0.1:18793:18789
#   → 容器内网关监听 18793 (env var)，但 Docker 只转发到 18789
#   → 127.0.0.1 绑定导致外部无法访问
# FIX: 改为 0.0.0.0:18793:18793
# ──────────────────────────────────────────────────────────────
log_step "5/8" "🔧 修复 docker-compose.yml..."

echo "  修复前端口配置:"
grep -n "1879" "$COMPOSE_FILE" 2>/dev/null || echo "  (未找到)"

# 精确替换端口映射行
sed -i 's|"127\.0\.0\.1:18793:18789"|"0.0.0.0:18793:18793"|g' "$COMPOSE_FILE"
sed -i "s|127\.0\.0\.1:18793:18789|\"0.0.0.0:18793:18793\"|g" "$COMPOSE_FILE"

# 同时修复注释
sed -i 's|# OpenClaw Dashboard (Local Access Only via Tunnel)|# OpenClaw Dashboard (LAN + Token Auth)|g' "$COMPOSE_FILE"

echo "  修复后端口配置:"
grep -n "1879" "$COMPOSE_FILE" 2>/dev/null || echo "  (未找到)"
log_ok "端口映射: 0.0.0.0:18793:18793"

# ──────────────────────────────────────────────────────────────
# STEP 6: 全盘搜索消失的 Skills
# ──────────────────────────────────────────────────────────────
log_step "6/8" "🔍 搜索消失的 Skills..."

echo ""
echo -e "${YELLOW}--- A. 当前挂载点 skills 目录 ---${NC}"
if [ -d "${DATA_DIR}/skills" ]; then
    CURRENT_COUNT=$(find "${DATA_DIR}/skills" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l)
    echo "  路径: ${DATA_DIR}/skills"
    echo "  当前 Skill 数量: $CURRENT_COUNT"
    ls "${DATA_DIR}/skills/" 2>/dev/null || true
else
    echo "  ⚠️ skills 目录不存在"
    mkdir -p "${DATA_DIR}/skills"
fi

echo ""
echo -e "${YELLOW}--- B. 全盘搜索所有 skills 目录 ---${NC}"
find / -maxdepth 5 -type d -name "skills" 2>/dev/null | while read dir; do
    count=$(find "$dir" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l)
    if [ "$count" -gt 0 ]; then
        echo -e "  📁 ${GREEN}$dir${NC} → Skill 数: $count"
        ls "$dir" 2>/dev/null | head -10
        if [ "$count" -gt 10 ]; then
            echo "  ... (还有 $((count-10)) 个)"
        fi
    fi
done

echo ""
echo -e "${YELLOW}--- C. Docker 命名卷搜索 ---${NC}"
docker volume ls --format "{{.Name}}" 2>/dev/null | while read vol; do
    echo -n "  卷 [$vol]: "
    RESULT=$(docker run --rm -v "${vol}:/mnt" alpine sh -c \
        'if [ -d /mnt/skills ]; then
            count=$(ls -d /mnt/skills/*/ 2>/dev/null | wc -l);
            echo "🎯 发现 skills! 包含 ${count} 个";
        else
            echo "无 skills";
        fi' 2>/dev/null) || RESULT="无法检查"
    echo "$RESULT"
done

echo ""
echo -e "${YELLOW}--- D. SKILL.md 全文检索 (Skill 标识文件) ---${NC}"
SKILL_MD_PATHS=$(find / -maxdepth 6 -name "SKILL.md" -type f 2>/dev/null)
SKILL_MD_COUNT=$(echo "$SKILL_MD_PATHS" | grep -c "." 2>/dev/null || echo "0")
echo "  找到 SKILL.md 文件: $SKILL_MD_COUNT 个"
if [ "$SKILL_MD_COUNT" -gt 0 ]; then
    echo "$SKILL_MD_PATHS" | while read p; do
        parent=$(dirname "$p")
        echo "  📄 $p"
    done
fi

echo ""
echo -e "${YELLOW}--- E. Docker overlay2 残留检查 ---${NC}"
OVERLAY_SKILLS=$(find /var/lib/docker/overlay2 -maxdepth 6 -type d -name "skills" 2>/dev/null | head -10)
if [ -n "$OVERLAY_SKILLS" ]; then
    echo "$OVERLAY_SKILLS" | while read dir; do
        count=$(find "$dir" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l)
        if [ "$count" -gt 2 ]; then
            echo -e "  🎯 ${GREEN}$dir${NC} → $count 个子目录 (可能是旧 Skills!)"
        fi
    done
else
    echo "  未在 overlay2 中找到 skills 目录"
fi

echo ""
echo -e "${YELLOW}--- F. 搜索其他 .openclaw 目录 ---${NC}"
find / -maxdepth 4 -type d -name ".openclaw" 2>/dev/null | while read dir; do
    if [ -d "$dir/skills" ]; then
        count=$(find "$dir/skills" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l)
        echo -e "  🎯 ${GREEN}$dir/skills${NC} → $count 个 Skills"
    else
        echo "  📁 $dir (无 skills 子目录)"
    fi
done

# ──────────────────────────────────────────────────────────────
# STEP 7: 重启（需要 rebuild 因为 entrypoint 在镜像里）
# ──────────────────────────────────────────────────────────────
log_step "7/8" "🚀 重构并启动容器..."
cd "$OPENCLAW_DIR"

# --build 确保使用最新的 entrypoint.sh 和 Dockerfile
docker compose up -d --build 2>/dev/null || docker-compose up -d --build 2>/dev/null || {
    log_err "docker compose up 失败!"
    echo "  尝试不 build 直接拉起..."
    docker compose up -d 2>/dev/null || docker-compose up -d 2>/dev/null
}

echo ""
echo "  ⏳ 等待 60 秒让容器完全启动..."
for i in $(seq 1 12); do
    sleep 5
    STATUS=$(docker inspect --format='{{.State.Status}}' openclaw_core 2>/dev/null || echo "unknown")
    echo -ne "\r  [$((i*5))/60s] 容器状态: $STATUS"
    if [ "$STATUS" = "running" ]; then
        # 额外等待 15 秒让内部服务初始化
        echo ""
        echo "  容器已 running，额外等待 15 秒..."
        sleep 15
        break
    fi
    if [ "$STATUS" = "restarting" ] && [ $i -ge 6 ]; then
        echo ""
        log_err "容器仍在重启循环! 查看日志..."
        docker logs openclaw_core --tail 30 2>&1
        echo ""
        log_warn "请检查上面的日志，找到错误原因后手动修复"
        break
    fi
done

echo ""
echo -e "${YELLOW}--- 容器状态 ---${NC}"
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null

echo ""
echo -e "${YELLOW}--- openclaw_core 日志 (最后 80 行) ---${NC}"
docker logs openclaw_core --tail 80 2>&1 || echo "(无日志)"

# ──────────────────────────────────────────────────────────────
# STEP 8: 设备审批
# ──────────────────────────────────────────────────────────────
log_step "8/8" "📱 设备审批状态..."

echo ""
echo "  尝试列出设备..."
docker exec openclaw_core openclaw devices list 2>&1 || {
    log_warn "无法执行 devices list (容器可能未就绪)"
    echo "  请等容器稳定后手动执行:"
    echo "    docker exec openclaw_core openclaw devices list"
    echo "    docker exec openclaw_core openclaw devices approve <ID>"
}

# ──────────────────────────────────────────────────────────────
# 最终报告
# ──────────────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}============================================================${NC}"
echo -e "${CYAN}  🏁 修复执行完毕！${NC}"
echo -e "${CYAN}============================================================${NC}"
echo ""
echo -e "${GREEN}📌 后续操作:${NC}"
echo ""
echo "  1. 浏览器访问 Dashboard:"
echo "     http://43.153.199.229:18793/#token=${GATEWAY_AUTH_TOKEN}"
echo ""
echo "  2. 如果需要 Token 登录:"
echo "     网关 Token: ${GATEWAY_AUTH_TOKEN}"
echo "     URL 直达: http://43.153.199.229:18793/#token=${GATEWAY_AUTH_TOKEN}"
echo ""
echo "  3. Chrome 安全上下文修复 (如果黑屏):"
echo "     chrome://flags/#unsafely-treat-insecure-origin-as-secure"
echo "     添加: http://43.153.199.229:18793"
echo "     (注意: Flags 里只填 origin，不带 #token 部分)"
echo "     设为 Enabled → 重启 Chrome"
echo ""
echo "  4. 需要审批新设备时:"
echo "     docker exec openclaw_core openclaw devices list"
echo "     docker exec openclaw_core openclaw devices approve <REQUEST_ID>"
echo "     ⚠️  注意: --all 参数在 2026.x 不可用"
echo ""
echo "  5. 如果容器仍在 Restarting 循环:"
echo "     docker logs openclaw_core --tail 100"
echo "     将错误日志发给我分析"
echo ""
echo "  6. 腾讯云防火墙 (极易遗漏!):"
echo "     Lighthouse 控制台 → 防火墙 → 添加入站规则:"
echo "     协议: TCP  端口: 18793  来源: 0.0.0.0/0"
echo ""
echo -e "${CYAN}============================================================${NC}"
