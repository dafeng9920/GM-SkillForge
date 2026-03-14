#!/usr/bin/env python3
"""
简化的后端启动脚本
用于测试L4 API是否正常工作
"""

import sys
import os
from pathlib import Path

# 添加项目路径到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "skillforge" / "src"))

try:
    # 尝试导入FastAPI应用
    from skillforge.src.api.l4_api import app
    print("✓ 成功导入L4 API应用")
    
    # 启动服务器
    import uvicorn
    print("启动后端服务器...")
    print("前端地址: http://localhost:5173")
    print("后端地址: http://localhost:8000")
    print("API健康检查: http://localhost:8000/api/v1/health")
    print("按 Ctrl+C 停止服务器")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请检查以下依赖是否已安装:")
    print("  pip install fastapi uvicorn python-multipart")
    sys.exit(1)
except Exception as e:
    print(f"❌ 启动错误: {e}")
    sys.exit(1)