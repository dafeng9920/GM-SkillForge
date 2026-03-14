#!/usr/bin/env python3
"""
直接运行L4 API服务器
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 导入并运行API
try:
    from skillforge.src.api.l4_api_fixed import app
    import uvicorn
    
    print("✅ 成功导入L4 API")
    print("🚀 启动服务器...")
    print("前端地址: http://localhost:5173")
    print("后端地址: http://localhost:8001")
    print("API健康检查: http://localhost:8001/api/v1/health")
    print("按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=False)
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("正在使用简化版API...")
    
    # 回退到简化版API
    from simple_api import app
    import uvicorn
    
    print("✅ 使用简化版API")
    print("🚀 启动服务器...")
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=False)
    
except Exception as e:
    print(f"❌ 启动错误: {e}")
    sys.exit(1)