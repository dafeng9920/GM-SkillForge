"""
A股量化交易系统 - 快速安装脚本

自动安装所有必要的依赖包

使用方法:
    python setup_trading_system.py
"""

import subprocess
import sys


def install_package(package: str):
    """安装单个包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False


def check_package(package_name: str, import_name: str = None):
    """检查包是否已安装"""
    if import_name is None:
        import_name = package_name

    try:
        __import__(import_name)
        return True
    except ImportError:
        return False


def main():
    """主安装流程"""
    print("=" * 70)
    print("  A股量化交易系统 - 依赖安装")
    print("=" * 70)

    # 核心依赖
    print("\n📦 检查核心依赖...")
    core_packages = [
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("akshare", "akshare"),
    ]

    missing_core = []
    for package_name, import_name in core_packages:
        if check_package(package_name, import_name):
            print(f"  ✓ {package_name}")
        else:
            print(f"  ✗ {package_name} - 需要安装")
            missing_core.append(package_name)

    # Web界面依赖
    print("\n🌐 检查Web界面依赖...")
    web_packages = [
        ("streamlit", "streamlit"),
        ("plotly", "plotly"),
    ]

    missing_web = []
    for package_name, import_name in web_packages:
        if check_package(package_name, import_name):
            print(f"  ✓ {package_name}")
        else:
            print(f"  ✗ {package_name} - 需要安装")
            missing_web.append(package_name)

    # 安装缺失的包
    if missing_core:
        print(f"\n🔧 安装核心依赖: {', '.join(missing_core)}")
        for package in missing_core:
            print(f"\n  安装 {package}...")
            if install_package(package):
                print(f"  ✓ {package} 安装成功")
            else:
                print(f"  ✗ {package} 安装失败")
                return False

    if missing_web:
        print(f"\n🔧 安装Web界面依赖: {', '.join(missing_web)}")
        for package in missing_web:
            print(f"\n  安装 {package}...")
            if install_package(package):
                print(f"  ✓ {package} 安装成功")
            else:
                print(f"  ✗ {package} 安装失败")

    print("\n" + "=" * 70)
    print("  ✅ 安装完成！")
    print("=" * 70)

    print("\n📚 下一步:")
    print("  1. 运行演示: python adapters/quant/trading/demo_trading_system.py")
    print("  2. 运行一次: python adapters/quant/trading/start_trading.py --once")
    print("  3. Web界面: python adapters/quant/trading/start_trading.py --web")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 安装被中断")
    except Exception as e:
        print(f"\n❌ 安装失败: {e}")
        sys.exit(1)
