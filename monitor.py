# monitor.py
import json
import os
from pathlib import Path

# 已通知账号记录文件
NOTIFIED_FILE = "notified_accounts.json"

def load_notified_accounts():
    """加载已通知的账号ID"""
    if os.path.exists(NOTIFIED_FILE):
        with open(NOTIFIED_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_notified_account(account_id):
    """保存已通知的账号ID"""
    notified = load_notified_accounts()
    notified.add(account_id)
    with open(NOTIFIED_FILE, 'w') as f:
        json.dump(list(notified), f)

def check_and_notify():
    # 获取新账号列表
    new_accounts = fetch_accounts()  # 你的获取逻辑
    
    # 过滤已通知的
    notified = load_notified_accounts()
    unnotified = [acc for acc in new_accounts if acc['id'] not in notified]
    
    if unnotified:
        # 保存这些账号ID
        for account in unnotified:
            save_notified_account(account['id'])
        
        # 生成通知内容
        print(f"发现 {len(unnotified)} 个新账号")
        # 退出码 1 触发邮件
        exit(1)
    else:
        print("没有新账号")
        exit(0)
