import os
import json
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class IntelAnalyzer:
    """
    认知层：将碎片化的抓取数据转化为人类可读的商业情报。
    """
    
    def __init__(self):
        # 兼容 GLM-4/5 (智谱 AI) 或其他 OpenAI-like 接口
        self.api_key = os.getenv("ZHIPU_API_KEY") or os.getenv("GLM_API_KEY")
        self.api_base = os.getenv("ZHIPU_API_BASE", "https://open.bigmodel.cn/api/paas/v4")
        self.model = os.getenv("GLM_MODEL", "glm-4")
        
    def analyze_kol_data(self, user: str, raw_data: List[Dict[str, Any]]) -> str:
        """
        通过 GLM 引擎分析 KOL 的推文内容及互动数据。
        """
        if not raw_data:
            return "⚠️ 未发现有效数据，无法进行情报分析。"
            
        # 1. 构建 Prompt (保持原有的商业深度)
        context = "\n---\n".join([
            f"内容: {item['text']}\n互动: {json.dumps(item['engagement'])}" 
            for item in raw_data[:15]
        ])
        
        system_prompt = f"""
你是一位世界顶级的商业分析师和产品经理，擅长从独立开发者（Indie Hackers）和技术领袖（KOL）的言论中提取“含金量”最高的信息。
你的任务是分析 @{user} 最近的推文，并输出一份逻辑严密的《商业决策内参》。

要求：
1. **去噪**：忽略日常琐事，聚焦于商业模式、技术趋势、利基市场发现和人生底层逻辑。
2. **量化**：结合互动数据（Likes/Retweets）指出哪条信息最具爆火潜力和社会共鸣。
3. **行动建议**：如果是我们要模仿或学习他，今晚可以落地的一个动作是什么。
4. **排版**：使用 Markdown 格式，保持专业、犀利、简洁。
        """
        
        user_prompt = f"这是 @{user} 最近抓取到的原始数据：\n\n{context}\n\n请开始你的专业分析："

        # 2. 调用符合 OpenAI 协议的 GLM 接口
        try:
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False
            }
            
            response = requests.post(f"{self.api_base}/chat/completions", headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                return f"❌ 情报引擎分析失败: HTTP {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"❌ 发生异常: {str(e)}"

if __name__ == "__main__":
    # 测试代码：读取最近一次抓取的 JSON
    # 假设我们手动跑了一次采集并拿到了 data
    import sys
    from scraper_interface import StealthScraperInterface
    
    analyzer = IntelAnalyzer()
    scraper = StealthScraperInterface()
    
    target = "levelsio"
    print(f"正在为 @{target} 开启潜行采集...")
    scrape_res = scraper.scrape_x_user(target, depth=3)
    
    if scrape_res.get("status") == "success":
        print(f"采集成功，抓获 {scrape_res.get('total_captured')} 条数据。正在启动 AI 分析层...")
        insight = analyzer.analyze_kol_data(target, scrape_res.get("data", []))
        print("\n" + "="*50)
        print(f"💎 @{target} 商业情报内参")
        print("="*50 + "\n")
        print(insight)
    else:
        print(f"采集环节失败: {scrape_res.get('reason')}")
