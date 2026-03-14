#!/usr/bin/env python3
"""
启动完整版L4 API服务器
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

def check_port(port):
    """检查端口是否被占用"""
    try:
        response = requests.get(f"http://127.0.0.1:{port}/api/v1/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    print("🚀 启动SkillForge L4 完整版API服务器...")
    
    # 检查8001端口是否被占用
    if check_port(8001):
        print("⚠️  端口8001已被占用，尝试停止现有服务...")
        try:
            subprocess.run(["taskkill", "/F", "/IM", "python.exe"], 
                         capture_output=True, check=False)
            time.sleep(2)
        except:
            pass
    
    # 启动API服务器
    api_file = Path("skillforge/src/api/l4_api_fixed.py")
    if not api_file.exists():
        print("❌ API文件不存在:", api_file)
        sys.exit(1)
    
    print("📡 启动API服务器...")
    print("前端地址: http://localhost:5173")
    print("后端地址: http://localhost:8001")
    print("API健康检查: http://localhost:8001/api/v1/health")
    print("按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    try:
        # 启动uvicorn服务器
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "skillforge.src.api.l4_api_fixed:app",
            "--host", "127.0.0.1",
            "--port", "8001",
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        print("请确保已安装依赖: pip install fastapi uvicorn")
        sys.exit(1)

if __name__ == "__main__":
    main()