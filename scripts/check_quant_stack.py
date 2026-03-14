"""
Quant System 基础设施健康检查脚本

Phase 0: 验证所有基础设施组件是否正常运行
"""

import sys
import time
import psycopg2
import redis
from datetime import datetime

# 服务配置
SERVICES = {
    "postgresql": {
        "host": "localhost",
        "port": 5432,
        "database": "quant_meta",
        "user": "quant_admin",
        "password": "quant_secure_change_me",
    },
    "redis": {
        "host": "localhost",
        "port": 6379,
        "db": 0,
    },
    "tdengine": {
        "host": "localhost",
        "port": 6030,
    },
    "minio": {
        "endpoint": "http://localhost:9000",
        "access_key": "minioadmin",
        "secret_key": "minioadmin_change_me",
    },
}


class HealthChecker:
    """健康检查器"""

    def __init__(self):
        self.results = {}

    def check_postgresql(self):
        """检查PostgreSQL连接"""
        try:
            conn = psycopg2.connect(
                host=SERVICES["postgresql"]["host"],
                port=SERVICES["postgresql"]["port"],
                database=SERVICES["postgresql"]["database"],
                user=SERVICES["postgresql"]["user"],
                password=SERVICES["postgresql"]["password"],
            )
            cursor = conn.cursor()

            # 检查表是否存在
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_schema IN ('quant_config', 'quant_data', 'quant_audit')
            """)
            table_count = cursor.fetchone()[0]

            cursor.close()
            conn.close()

            self.results["postgresql"] = {
                "status": "healthy",
                "tables": table_count,
                "message": f"连接成功，发现{table_count}个表"
            }
            return True

        except Exception as e:
            self.results["postgresql"] = {
                "status": "unhealthy",
                "error": str(e),
                "message": "连接失败"
            }
            return False

    def check_redis(self):
        """检查Redis连接"""
        try:
            r = redis.Redis(
                host=SERVICES["redis"]["host"],
                port=SERVICES["redis"]["port"],
                db=SERVICES["redis"]["db"],
                decode_responses=True,
            )

            # 测试连接
            info = r.info()
            memory_used = info.get("used_memory_human", "unknown")

            self.results["redis"] = {
                "status": "healthy",
                "memory": memory_used,
                "message": f"连接成功，内存使用: {memory_used}"
            }
            return True

        except Exception as e:
            self.results["redis"] = {
                "status": "unhealthy",
                "error": str(e),
                "message": "连接失败"
            }
            return False

    def check_tdengine(self):
        """检查TDengine连接"""
        try:
            import subprocess

            # 使用docker执行taos命令
            result = subprocess.run(
                ["docker", "exec", "quant-tdengine", "taos", "-s", "tdengine"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                self.results["tdengine"] = {
                    "status": "healthy",
                    "message": "连接成功"
                }
                return True
            else:
                raise Exception(result.stderr)

        except Exception as e:
            self.results["tdengine"] = {
                "status": "unhealthy",
                "error": str(e),
                "message": "连接失败"
            }
            return False

    def check_minio(self):
        """检查MinIO连接"""
        try:
            import requests

            # 检查健康状态
            response = requests.get(
                f"{SERVICES['minio']['endpoint']}/minio/health/live",
                timeout=5,
            )

            if response.status_code == 200:
                self.results["minio"] = {
                    "status": "healthy",
                    "message": "连接成功"
                }
                return True
            else:
                raise Exception(f"HTTP {response.status_code}")

        except Exception as e:
            self.results["minio"] = {
                "status": "unhealthy",
                "error": str(e),
                "message": "连接失败"
            }
            return False

    def run_all_checks(self):
        """运行所有健康检查"""
        print("\n" + "=" * 70)
        print("Quant System 基础设施健康检查")
        print("=" * 70)
        print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("")

        checks = [
            ("PostgreSQL", self.check_postgresql),
            ("Redis", self.check_redis),
            ("TDengine", self.check_tdengine),
            ("MinIO", self.check_minio),
        ]

        passed = 0
        total = len(checks)

        for name, check_func in checks:
            print(f"检查 {name}...", end=" ")
            if check_func():
                print("✓ " + self.results[name.lower()]["message"])
                passed += 1
            else:
                print("✗ " + self.results[name.lower()]["message"])

        # 打印汇总
        print("\n" + "=" * 70)
        print("健康检查汇总")
        print("=" * 70)
        print(f"总计: {passed}/{total} 通过")

        if passed == total:
            print("\n🎉 所有服务正常运行！")
            print("\n下一步操作:")
            print("  1. 初始化Skill数据: python scripts/init_skill_data.py")
            print("  2. 开始Phase 1: 数据层Skills实现")
            return True
        else:
            print("\n⚠️  部分服务异常，请检查Docker容器状态")
            print("  运行: docker-compose -f docker/quant-stack.yml ps")
            return False


def main():
    """主函数"""
    checker = HealthChecker()
    success = checker.run_all_checks()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
