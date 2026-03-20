import requests
import json
import logging
from typing import Dict, Any, Optional

class StealthScraperInterface:
    """
    AIOScannerCore 专用：Stealth Scraper Core 的宿主机调用封装。
    使 Xiaolongxia 核心能像调用本地函数一样驱动 Docker 爬虫。
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.logger = logging.getLogger("StealthScraper")

    def check_health(self) -> bool:
        """检查爬虫引擎是否在线 (轻量级)"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            return response.json().get("status") == "ok"
        except Exception as e:
            self.logger.error(f"Scraper Engine Offline: {e}")
            return False

    def scrape_x_user(self, target_user: str, depth: int = 5, proxy: Optional[str] = None) -> Dict[str, Any]:
        """
        抓取指定 X 用户的内容与互动指标。
        """
        params = {"target_user": target_user, "depth": depth}
        if proxy:
            params["proxy"] = proxy
            
        try:
            self.logger.info(f"Initiating deep scrape for X user: @{target_user} (depth: {depth})")
            response = requests.get(f"{self.base_url}/v1/scrape/x", params=params, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    self.logger.info(f"Successfully captured {result.get('total_captured')} posts from @{target_user}")
                else:
                    self.logger.warning(f"Scrape completed with issues: {result.get('reason')}")
                return result
            else:
                return {
                    "status": "error", 
                    "reason": f"HTTP {response.status_code}", 
                    "detail": response.text
                }
                
        except requests.exceptions.Timeout:
            return {"status": "error", "reason": "TIMEOUT", "detail": "Engine response too slow, check GPU/Network"}
        except Exception as e:
            return {"status": "error", "reason": "EXCEPTION", "detail": str(e)}

if __name__ == "__main__":
    # 快速验证脚本
    scraper = StealthScraperInterface()
    if scraper.check_health():
        print("Scraper Engine Status: [READY]")
        # 尝试抓取一次
        res = scraper.scrape_x_user("elonmusk", depth=3)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print("Scraper Engine Status: [OFFLINE] - Please run docker-compose up")
