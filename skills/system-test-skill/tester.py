"""System Test - 系统测试"""

from .tester import SystemTestSuite, TestResult

__all__ = ["SystemTestSuite", "TestResult"]


class TestResult:
    """测试结果"""
    def __init__(self, name, status, duration, message=""):
        self.name = name
        self.status = status  # PASS, FAIL, SKIP
        self.duration = duration
        self.message = message


class SystemTestSuite:
    """系统测试套件"""

    def __init__(self):
        self._tests = []
        self._results = []

    def add_test(self, test_func, name=""):
        """添加测试"""
        self._tests.append((test_func, name))

    async def run_all(self):
        """运行所有测试"""
        self._results = []

        for test_func, name in self._tests:
            try:
                import time
                start = time.time()
                await test_func()
                duration = time.time() - start

                self._results.append(TestResult(
                    name=name or test_func.__name__,
                    status="PASS",
                    duration=duration,
                ))
            except Exception as e:
                self._results.append(TestResult(
                    name=name or test_func.__name__,
                    status="FAIL",
                    duration=0,
                    message=str(e),
                ))

        return self._results

    def get_summary(self):
        """获取测试摘要"""
        total = len(self._results)
        passed = sum(1 for r in self._results if r.status == "PASS")
        failed = sum(1 for r in self._results if r.status == "FAIL")

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / total if total > 0 else 0,
        }
