import os
import shutil

# -------------------------- 配置参数（根据需求修改）--------------------------
# ETF 数据文件所在目录（替换为你的实际路径）
SOURCE_DIR = r"C:\data-center-pro\stock-etf-trading-data"
# 是否覆盖目标文件夹中已存在的同名文件（True=覆盖，False=跳过）
OVERWRITE = False
# -----------------------------------------------------------------------------

# -------------------------- A股ETF类型-代码映射（严格遵循分类规则）--------------------------
# 键：ETF类型名称，值：该类型对应的代码开头（列表形式，支持多个开头）
ETF_TYPE_CODE_MAP = {
    "宽基ETF": ["510", "1599"],          # 上交所510xx、深交所1599xx
    "行业ETF": ["512", "1598"],          # 上交所512xx、深交所1598xx
    "主题ETF": ["515", "516", "1596"],   # 上交所515/516xx、深交所1596xx（龙头/普通主题）
    "商品ETF": ["518", "519", "159934", "159981"],  # 上交所518/519xx、深交所特殊商品代码
    "债券ETF": ["511", "159616", "159637"],  # 上交所511xx、深交所可转债/国债ETF特殊代码
    "跨境ETF": ["513", "1597"],          # 上交所513xx、深交所1597xx（跟踪海外）
    "货币ETF": ["511990", "159001", "511880"]  # 货币ETF无统一开头，直接列核心代码
}

# 未匹配到类型的ETF会放入此文件夹
OTHER_TYPE_DIR = "其他ETF"

def get_etf_type(etf_code):
    """根据ETF代码判断类型（核心匹配函数）"""
    for etf_type, code_prefixes in ETF_TYPE_CODE_MAP.items():
        # 匹配规则：代码以指定前缀开头，或完全等于指定代码（如货币ETF特殊代码）
        if any(etf_code.startswith(prefix) or etf_code == prefix for prefix in code_prefixes):
            return etf_type
    return OTHER_TYPE_DIR

def classify_etf_files():
    # 1. 检查源目录是否存在
    if not os.path.exists(SOURCE_DIR):
        print(f"错误：源目录不存在 → {SOURCE_DIR}")
        return

    # 2. 遍历源目录下所有CSV文件
    total_files = 0
    success_count = 0
    skip_count = 0
    error_count = 0

    for filename in os.listdir(SOURCE_DIR):
        # 只处理CSV文件，且文件名格式为「代码.市场.csv」（如159001.SZ.csv）
        if filename.endswith(".csv") and len(filename.split(".")) >= 2:
            total_files += 1
            # 提取ETF代码（文件名第一个部分，如159001.SZ.csv → 159001）
            etf_code = filename.split(".")[0]
            # 验证代码是否为6位数字（A股ETF代码均为6位）
            if not etf_code.isdigit() or len(etf_code) != 6:
                print(f"跳过：文件名格式异常 → {filename}（代码应为6位数字）")
                skip_count += 1
                continue

            # 3. 判断ETF类型
            etf_type = get_etf_type(etf_code)
            # 创建目标文件夹（如「宽基ETF」）
            target_dir = os.path.join(SOURCE_DIR, etf_type)
            os.makedirs(target_dir, exist_ok=True)

            # 4. 定义源文件路径和目标文件路径
            source_path = os.path.join(SOURCE_DIR, filename)
            target_path = os.path.join(target_dir, filename)

            # 5. 处理文件移动（避免覆盖）
            try:
                if os.path.exists(target_path):
                    if OVERWRITE:
                        shutil.move(source_path, target_path)  # 覆盖已存在文件
                        print(f"覆盖：{filename} → {etf_type}")
                        success_count += 1
                    else:
                        print(f"跳过：{filename} → {etf_type}（目标文件已存在）")
                        skip_count += 1
                else:
                    shutil.move(source_path, target_path)  # 移动新文件
                    print(f"成功：{filename} → {etf_type}")
                    success_count += 1
            except Exception as e:
                print(f"错误：移动{filename}失败 → {str(e)}")
                error_count += 1

    # 6. 输出统计结果
    print("\n" + "-"*50)
    print(f"分类完成！统计结果：")
    print(f"总处理文件数：{total_files}")
    print(f"成功移动：{success_count}")
    print(f"跳过文件：{skip_count}")
    print(f"移动失败：{error_count}")
    print(f"分类文件夹路径：{SOURCE_DIR}")
    print("-"*50)

if __name__ == "__main__":
    classify_etf_files()