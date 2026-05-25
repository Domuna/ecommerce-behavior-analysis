import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("未找到 API Key，请检查 .env 文件配置")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

anomaly_category = {
    "category_id": "154040",
    "pv": 8883,
    "cart_and_fav": 508,
    "buy": 29,
    "conversion_rate": "0.35%"
}

system_prompt = """
你是一个拥有 10 年经验的资深阿里电商数据运营专家。
你的任务是根据提供的数据，诊断转化率低下的原因，并给出可落地的运营策略。
请务必以纯 JSON 格式输出，包含 "root_causes" (列表格式，最多3条) 和 "action_items" (列表格式，最多3条) 两个字段。
"""

user_prompt = f"""
我正在分析一份淘宝千万级用户行为抽样数据。发现以下品类存在严重的漏斗异常（高曝光、极低转化）：
品类ID: {anomaly_category['category_id']}
总浏览量(PV): {anomaly_category['pv']}
加购与收藏总量: {anomaly_category['cart_and_fav']}
实际购买量: {anomaly_category['buy']}
最终购买转化率: {anomaly_category['conversion_rate']}

请分析导致该现象的核心原因，并给出具体的运营干预动作。
"""

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    response_format={"type": "json_object"},
    temperature=0.7
)


result_json_str = response.choices[0].message.content
result_dict = json.loads(result_json_str)

print("========== AI 运营分析报告 ==========")
print(f"分析目标品类: {anomaly_category['category_id']}")
print("-" * 35)

print("【异常根因诊断】:")
for i, cause in enumerate(result_dict.get("root_causes", []), 1):
    print(f"{i}. {cause}")

print("\n【业务干预策略】:")
for i, action in enumerate(result_dict.get("action_items", []), 1):
    print(f"{i}. {action}")