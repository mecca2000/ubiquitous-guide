#!/usr/bin/env python3
"""
A股极速报告 - 针对特定股票快速输出
"""

import requests
import sys

def get_stock_fast(code, market='sh'):
    """极简获取，最快响应"""
    url = f"https://hq.sinajs.cn/list={market}{code}"
    headers = {'Referer': 'https://finance.sina.com.cn'}
    try:
        r = requests.get(url, headers=headers, timeout=3)
        r.encoding = 'gb2312'
        data = r.text.split('=')[1].strip().strip('";').split(',')
        name = data[0]
        current = float(data[3])
        prev = float(data[2])
        change = ((current - prev) / prev) * 100
        amount = float(data[9]) / 100000000
        return name, current, change, amount
    except:
        return None, None, None, None

def analyze(codes_list):
    """codes_list: [(code, name, market), ...]"""
    print("📊 A股快照")
    print("-" * 50)
    
    for code, name, market in codes_list:
        n, p, c, a = get_stock_fast(code, market)
        if n:
            trend = "🟢" if c > 0 else "🔴" if c < 0 else "⚪"
            status = "强" if abs(c) > 2 else "中" if abs(c) > 0.5 else "弱"
            print(f"{trend} {name}: ¥{p:.2f} ({c:+.2f}%) [{status}] {a:.1f}亿")
        else:
            print(f"⚠️ {name}: 失败")
    
    print("-" * 50)

if __name__ == '__main__':
    # 默认分析券商+持仓
    default_stocks = [
        ('300059', '东方财富', 'sz'),
        ('300803', '指南针', 'sz'),
        ('600309', '万华化学', 'sh'),
        ('002463', '沪电股份', 'sz'),
    ]
    analyze(default_stocks)
