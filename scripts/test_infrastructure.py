"""
基础设施测试脚本

验证PostgreSQL、Redis、TDengine、MinIO是否正常工作
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_postgresql():
    """测试PostgreSQL连接"""
    try:
        import psycopg2

        print("测试 PostgreSQL 连接...")
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='quant_meta',
            user='quant_admin',
            password='quant_secure_change_me',
        )

        cursor = conn.cursor()

        # 检查表是否存在
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema IN ('quant_config', 'quant_data', 'quant_audit')
            ORDER BY table_schema, table_name
        """)

        tables = cursor.fetchall()

        print(f"  ✓ 连接成功")
        print(f"  发现 {len(tables)} 个表:")
        for schema, table in tables:
            print(f"    - {schema}.{table}")

        cursor.close()
        conn.close()

        return True

    except ImportError:
        print("  ✗ psycopg2未安装: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"  ✗ 连接失败: {e}")
        return False


def test_redis():
    """测试Redis连接"""
    try:
        import redis

        print("测试 Redis 连接...")
        r = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True,
        )

        # 测试连接
        info = r.info()
        used_memory = info.get('used_memory_human', 'unknown')

        # 设置测试键值
        r.set('test_key', 'test_value')
        value = r.get('test_key')
        r.delete('test_key')

        print(f"  ✓ 连接成功")
        print(f"  内存使用: {used_memory}")

        return True

    except ImportError:
        print("  ✗ redis未安装: pip install redis")
        return False
    except Exception as e:
        print(f"  ✗ 连接失败: {e}")
        return False


def test_tdengine():
    """测试TDengine连接"""
    try:
        import subprocess

        print("测试 TDengine 连接...")

        # 使用docker执行taos命令
        result = subprocess.run(
            ["docker", "exec", "quant-tdengine", "taos", "-s", "tdengine"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0:
            print("  ✓ 连接成功")
            return True
        else:
            print(f"  ✗ 连接失败: {result.stderr}")
            return False

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False


def test_minio():
    """测试MinIO连接"""
    try:
        import requests

        print("测试 MinIO 连接...")

        # 检查健康状态
        response = requests.get(
            "http://localhost:9000/minio/health/live",
            timeout=5,
        )

        if response.status_code == 200:
            print("  ✓ 连接成功")

            # 测试MinIO Python SDK
            try:
                from minio import Minio

                client = Minio(
                    'localhost:9001',
                    access_key='minioadmin',
                    secret_key='minioadmin_change_me',
                    secure=False,
                )

                # 列出buckets
                buckets = client.list_buckets()
                print(f"  发现 {len(buckets)} 个bucket:")
                for bucket in buckets:
                    print(f"    - {bucket.name}")

            except ImportError:
                print("  ⚠ MinIO SDK未安装: pip install minio")

            return True
        else:
            print(f"  ✗ 健康检查失败: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False


def test_docker_containers():
    """测试Docker容器状态"""
    try:
        import subprocess

        print("检查 Docker 容器状态...")
        result = subprocess.run(
            ["docker", "compose", "-f", "docker/quant-stack.yml", "ps"],
            capture_output=True,
            text=True,
        )

        print(result.stdout)

        # 检查是否有容器在运行
        if 'quant-' in result.stdout and 'Up' in result.stdout:
            print("  ✓ 容器运行正常")
            return True
        else:
            print("  ✗ 部分容器未运行")
            return False

    except Exception as e:
        print(f"  ✗ 检查失败: {e}")
        return False


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("Quant System 基础设施测试")
    print("=" * 70)
    print("")

    # 检查Docker容器
    containers_ok = test_docker_containers()
    print("")

    # 如果容器不正常，提示用户先启动
    if not containers_ok:
        print("\n请先启动基础设施:")
        print("  PowerShell: .\\scripts\\start_quant_stack.ps1")
        print("  Bash:      ./scripts/start_quant_stack.sh")
        return False

    # 测试各个服务
    tests = [
        ("PostgreSQL", test_postgresql),
        ("Redis", test_redis),
        ("TDengine", test_tdengine),
        ("MinIO", test_minio),
    ]

    passed = 0
    total = len(tests)

    for name, test_func in tests:
        print()
        if test_func():
            passed += 1

    # 打印汇总
    print("\n" + "=" * 70)
    print(f"测试结果: {passed}/{total} 通过")
    print("=" * 70)

    if passed == total:
        print("\n🎉 基础设施测试全部通过！")
        print("\n下一步: python -m pip install -r requirements/quant-system.txt")
        print("      然后开始Phase 1: 数据层Skills实现")
        return True
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查服务状态")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
