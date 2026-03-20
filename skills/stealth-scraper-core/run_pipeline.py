import json
import os
import time
from datetime import datetime
from scraper_interface import StealthScraperInterface
from intel_analyzer import IntelAnalyzer

def run_automated_pipeline():
    """
    自动化情报流水线：读取清单 -> 潜行抓取 -> AI 分析 -> 生成简报
    """
    KOL_FILE = "d:/GM-SkillForge/skills/stealth-scraper-core/KOL_LIST.json"
    REPORT_DIR = "d:/GM-SkillForge/skills/stealth-scraper-core/reports"
    
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)
        
    scraper = StealthScraperInterface()
    analyzer = IntelAnalyzer()
    
    # 1. 检查引擎状态
    if not scraper.check_health():
        print("❌ Scraper Engine Error: Please ensure Docker is running and GPU is accessible.")
        return

    # 2. 读取大佬清单
    try:
        with open(KOL_FILE, "r", encoding="utf-8") as f:
            kol_list = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load KOL list: {e}")
        return

    # 3. 循环执行
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    final_report_path = os.path.join(REPORT_DIR, f"FLASH_REPORT_{timestamp}.md")
    
    with open(final_report_path, "w", encoding="utf-8") as report_file:
        report_file.write(f"# 🚀 全球科技情报闪电简报 ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n\n")
        report_file.write("> 自动化等级：L3 (Stealth & AI Cognitive Layer)\n\n---\n")

        for kol in kol_list:
            handle = kol['handle']
            name = kol['name']
            print(f"📡 正在监控 [@{handle}] ({name})...")
            
            # 抓取 (设置较小的 depth 提高效率)
            res = scraper.scrape_x_user(handle, depth=2)
            
            if res.get("status") == "success":
                print(f"🧠 正在分析 @{handle} 的最新动态...")
                insight = analyzer.analyze_kol_data(handle, res.get("data", []))
                
                # 写入简报
                report_file.write(f"## 👤 {name} (@{handle}) - {kol['category']}\n")
                report_file.write(f"{insight}\n\n---\n")
                print(f"✅ @{handle} 情报已归档。")
            else:
                print(f"⚠️ @{handle} 抓取失败: {res.get('reason')}")
                report_file.write(f"## 👤 {name} (@{handle})\n> ❌ 采集状态：失败 ({res.get('reason')})\n\n---\n")
            
            # 防御性延迟，防止 IP 触发风控频率
            time.sleep(random.randint(30, 60) if 'random' in locals() else 30)

    print(f"\n✨ 任务全部完成！今日简报已生成：{final_report_path}")

if __name__ == "__main__":
    run_automated_pipeline()
