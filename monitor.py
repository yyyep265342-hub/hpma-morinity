#!/usr/bin/env python3
# monitor.py - 藏宝阁监控脚本（带去重通知）

import requests
import json
import sys
import os
from datetime import datetime

# 已通知账号记录文件
NOTIFIED_FILE = "notified_accounts.json"

# 你的筛选参数
PAYLOAD = {
    "client_type": "h5",
    "act": "recommd_by_role",
    "search_type": "role",
    "count": "15",
    "view_loc": "search_cond",
    "gender__or": "2",
    "card_list": '[{"card_list__id":"1198","card_list__level":15}]',
    "wand__and": "10000020",
    "rare_cloth__and": "10453621,10453821,10454011,10454025,10454059,10454122",
    "frame__or": "4101162",
    "order_by": "",
    "page": "1",
    "exter": "cbg.163.com",
}

def load_notified_accounts():
    """加载已通知的账号ID"""
    if os.path.exists(NOTIFIED_FILE):
        try:
            with open(NOTIFIED_FILE, 'r') as f:
                data = json.load(f)
                return set(data) if isinstance(data, list) else set()
        except:
            return set()
    return set()

def save_notified_accounts(account_ids):
    """保存已通知的账号ID列表"""
    with open(NOTIFIED_FILE, 'w') as f:
        json.dump(list(account_ids), f)

def fetch_accounts():
    """从藏宝阁获取账号列表"""
    try:
        resp = requests.post(
            "https://hp.cbg.163.com/cgi-bin/recommend.py?client_type=h5&act=recommd_by_role",
            data=PAYLOAD,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": "https://hp.cbg.163.com/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            timeout=15
        )
        
        if resp.status_code != 200:
            print(f"[{datetime.now()}] 请求失败，状态码: {resp.status_code}")
            return []
            
        data = resp.json()
        print(f"[{datetime.now()}] API返回数据: {json.dumps(data, ensure_ascii=False)[:300]}")
        
        # 根据实际返回结构提取账号列表
        results = data.get("result", [])
        if not results:
            results = data.get("data", {}).get("list", [])
        
        # 确保每个账号都有唯一标识（使用角色ID或商品ID）
        accounts = []
        for item in results:
            # 尝试多种可能的ID字段
            account_id = item.get("role_id") or item.get("id") or item.get("goods_id")
            if not account_id:
                # 如果都没有，用整个item的哈希值作为标识
                account_id = str(hash(json.dumps(item, sort_keys=True)))
            accounts.append({
                "id": str(account_id),
                "name": item.get("role_name") or item.get("name") or "未知",
                "price": item.get("price") or item.get("total_price") or 0
            })
        
        print(f"[{datetime.now()}] 获取到 {len(accounts)} 个账号")
        return accounts
        
    except Exception as e:
        print(f"[{datetime.now()}] 获取账号失败: {e}")
        return []

def check_and_notify():
    """主函数：检查并通知新账号"""
    print(f"[{datetime.now()}] 开始检查藏宝阁...")
    
    # 获取新账号列表
    new_accounts = fetch_accounts()
    
    if not new_accounts:
        print("未发现任何账号")
        sys.exit(0)
    
    # 加载已通知的账号
    notified = load_notified_accounts()
    print(f"已通知账号数: {len(notified)}")
    
    # 过滤出未通知的账号
    unnotified = [acc for acc in new_accounts if acc['id'] not in notified]
    
    if unnotified:
        # 打印新账号信息
        print(f"发现 {len(unnotified)} 个新账号：")
        for acc in unnotified:
            print(f"  - {acc['name']} (ID: {acc['id']}, 价格: {acc['price']})")
        
        # 保存这些新账号的ID（合并到已有集合）
        all_notified = notified.union({acc['id'] for acc in unnotified})
        save_notified_accounts(all_notified)
        
        # 将账号信息写入输出，供邮件使用
        account_summary = "\n".join([f"- {acc['name']} (¥{acc['price']})" for acc in unnotified])
        with open(os.environ.get("GITHUB_OUTPUT", "/tmp/output.txt"), "a") as f:
            f.write(f"accounts={len(unnotified)}\n")
            f.write(f"details={account_summary}\n")
        
        print(f"::notice::发现 {len(unnotified)} 个新账号！")
        # 退出码 1 触发邮件通知
        sys.exit(1)
    else:
        print("没有发现新账号（所有账号都已通知过）")
        sys.exit(0)

if __name__ == "__main__":
    check_and_notify()
