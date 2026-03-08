"""
Tests for AuditPackStore Initialization (M0/M2)

覆盖范围:
1. 在生产环境 (SKILLFORGE_ENV=prod) 下，空目录初始化时绝对不应该产生 dummy数据（防止语义污染）。
2. 在默认环境 (未设置 SKILLFORGE_ENV) 下，采用默认 prod 行为，不产生 dummy 数据。
3. 在 dev/test 环境下，空目录初始化时会产生 sample_packs，用于测试和脚手架。
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from storage.audit_pack_store import AuditPackStore

class TestAuditPackStoreInit(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = Path(self.temp_dir) / "audit_packs"
        
        # 保存原始的环境变量
        self.original_env = os.environ.get("SKILLFORGE_ENV")
        
    def tearDown(self):
        """Clean up test fixtures."""
        if self.original_env is not None:
            os.environ["SKILLFORGE_ENV"] = self.original_env
        else:
            os.environ.pop("SKILLFORGE_ENV", None)
            
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_default_env_no_dummy_data(self):
        """Test that default environment behaves like prod (Zero Dummy Data)."""
        # Ensure SKILLFORGE_ENV is not set
        os.environ.pop("SKILLFORGE_ENV", None)
        
        store = AuditPackStore(self.storage_path)
        # Calling public method triggers _ensure_initialized()
        store.fetch_by_run_id("dummy")
        
        # 必须是空的，不能有 dummy 数据
        self.assertEqual(len(os.listdir(self.storage_path)), 0)

    def test_prod_env_no_dummy_data(self):
        """Test that prod environment strictly enforces Zero Dummy Data."""
        os.environ["SKILLFORGE_ENV"] = "prod"
        
        store = AuditPackStore(self.storage_path)
        store.fetch_by_run_id("dummy")
        
        # 必须是空的，不能有 dummy 数据
        self.assertEqual(len(os.listdir(self.storage_path)), 0)
        
    def test_dev_env_creates_sample_packs(self):
        """Test that dev environment allows sample dummy data generation."""
        os.environ["SKILLFORGE_ENV"] = "dev"
        
        store = AuditPackStore(self.storage_path)
        store.fetch_by_run_id("dummy")
        
        # dev 环境下应该自动生成至少1条 dummy pack (.json文件)
        self.assertGreaterEqual(len(list(self.storage_path.glob("*.json"))), 1)

    def test_test_env_creates_sample_packs(self):
        """Test that test environment allows sample dummy data generation."""
        os.environ["SKILLFORGE_ENV"] = "test"
        
        store = AuditPackStore(self.storage_path)
        store.fetch_by_run_id("dummy")
        
        # test 环境下也应该自动生成 dummy pack
        self.assertGreaterEqual(len(list(self.storage_path.glob("*.json"))), 1)

if __name__ == "__main__":
    unittest.main(verbosity=2)
