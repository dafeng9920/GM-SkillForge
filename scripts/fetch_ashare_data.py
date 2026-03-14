import akshare as ak
import json
import os
from datetime import datetime

def fetch_market_snapshot():
    """
    抓取 A 股大盘行情快照与领涨板块数据。
    """
    print(f"[{datetime.now()}] 🚀 正在抓取 A 股行情快照...")
    
    snapshot = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "indices": {},
        "top_gainers": []
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            # 1. 获取主要指数数据 (上证, 深证, 创业板)
            df_indices = ak.stock_zh_index_spot_em()
            target_indices = {
                "sh000001": "上证指数",
                "sz399001": "深证成指",
                "sz399006": "创业板指"
            }
            
            for code, name in target_indices.items():
                row = df_indices[df_indices["代码"] == code[2:]] # 匹配代码
                if not row.empty:
                    snapshot["indices"][name] = {
                        "price": float(row.iloc[0]["最新价"]),
                        "change_pct": float(row.iloc[0]["涨跌幅"])
                    }

            # 2. 获取今日领涨行业板块 (Top 5)
            df_sectors = ak.stock_board_industry_name_em()
            df_sectors_sorted = df_sectors.sort_values(by="涨跌幅", ascending=False).head(5)
            
            for _, row in df_sectors_sorted.iterrows():
                snapshot["top_gainers"].append({
                    "sector": row["板块名称"],
                    "change_pct": float(row["涨跌幅"]),
                    "lead_stock": row["领涨股"]
                })
            
            # 如果成功，跳出循环
            if snapshot["indices"]:
                snapshot.pop("error", None)
                break

        except Exception as e:
            print(f"⚠️ 第 {attempt + 1} 次尝试失败: {e}")
            snapshot["error"] = str(e)
            if attempt < max_retries - 1:
                import time
                time.sleep(2)

    # 3. 存储到 Workspace 数据目录
    output_dir = os.path.join("openclaw-box", "workspace", "trading_data")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_file = os.path.join(output_dir, "snapshot.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 快照已存至: {output_file}")
    return output_file

if __name__ == "__main__":
    fetch_market_snapshot()
