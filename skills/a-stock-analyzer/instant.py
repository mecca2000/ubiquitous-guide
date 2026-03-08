#!/usr/bin/env python3
"""
A股瞬时分析 - 预加载缓存版本
启动时预加载数据，查询时直接返回
"""

import requests
import json
import os
from datetime import datetime

CACHE_FILE = '/tmp/stock_cache.json'

def preload_stocks():
    """预加载常用股票数据到缓存"""
    stocks = "sh600309,sz002463,sz300059,sz300803,sh000001,sz399001,sz399006"
    url = f"https://hq.sinajs.cn/list={stocks}"
    headers = {'Referer': 'https://finance.sina.com.cn'}
    
    try:
        r = requests.get(url, headers=headers, timeout=5)
        r.encoding = 'gb2312'
        
        data = {}
        for line in r.text.strip().split('\n'):
            if '=' in line and 'var hq_str_' in line:
                parts = line.split('=')
                code = parts[0].replace('var hq_str_', '')
                items = parts[1].strip().strip('";').split(',')
                if len(items) >= 33:
                    data[code] = {
                        'name': items[0],
                        'price': float(items[3]),
                        'prev': float(items[2]),
                        'high': float(items[4]),
                        'low': float(items[5]),
                        'amount': float(items[9]) / 100000000
                    }
        
        # 保存缓存
        with open(CACHE_FILE, 'w') as f:
            json.dump({'time': datetime.now().isoformat(), 'data': data}, f)
        
        return data
    except Exception as e:
        print(f"预加载失败: {e}")
        return {}

def get_cached():
    """获取缓存数据"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                cache = json.load(f)
                return cache.get('data', {})
        except:
            pass
    return preload_stocks()

def quick_report(stock_names):
    """stock_names: {'300059': ('东方财富', 'sz'), ...}"""
    data = get_cached()
    
    lines = []
    for code, (name, market) in stock_names.items():
        key = f"{market}{code}"
        if key in data:
            s = data[key]
            change = ((s['price'] - s['prev']) / s['prev']) * 100
            trend = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
            lines.append(f"{trend} {name}: ¥{s['price']:.2f} ({change:+.2f}%)")
    
    return '\n'.join(lines) if lines else "暂无数据"

if __name__ == '__main__':
    # 测试
    test_stocks = {
        '300059': ('东方财富', 'sz'),
        '300803': ('指南针', 'sz'),
        '600309': ('万华化学', 'sh'),
        '002463': ('沪电股份', 'sz')
    }
    print(quick_report(test_stocks))
