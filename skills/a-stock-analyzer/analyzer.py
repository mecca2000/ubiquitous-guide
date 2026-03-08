#!/usr/bin/env python3
"""
A股实时分析器 - 高速版本
预加载 + 缓存机制
"""

import requests
import json
import time
from datetime import datetime

class AStockAnalyzer:
    def __init__(self):
        self.cache = {}
        self.cache_time = 0
        self.cache_ttl = 60  # 缓存60秒
        
    def fetch_realtime(self, codes):
        """批量获取实时数据"""
        url = f"https://hq.sinajs.cn/list={codes}"
        headers = {
            'Referer': 'https://finance.sina.com.cn',
            'User-Agent': 'Mozilla/5.0'
        }
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            resp.encoding = 'gb2312'
            return self._parse_data(resp.text)
        except:
            return {}
    
    def _parse_data(self, text):
        """解析新浪数据"""
        results = {}
        for line in text.strip().split('\n'):
            if '=' in line and 'var hq_str_' in line:
                parts = line.split('=')
                code = parts[0].replace('var hq_str_', '')
                data = parts[1].strip().strip('";').split(',')
                if len(data) >= 33:
                    results[code] = {
                        'name': data[0],
                        'current': float(data[3]),
                        'prev': float(data[2]),
                        'change_pct': ((float(data[3]) - float(data[2])) / float(data[2])) * 100,
                        'high': float(data[4]),
                        'low': float(data[5]),
                        'volume': int(float(data[8])),
                        'amount': float(data[9]) / 100000000
                    }
        return results
    
    def get_stock(self, code, market='sh'):
        """获取单只股票（带缓存）"""
        full_code = f"{market}{code}"
        
        # 检查缓存
        if full_code in self.cache and (time.time() - self.cache_time) < self.cache_ttl:
            return self.cache[full_code]
        
        # 刷新缓存
        data = self.fetch_realtime(full_code)
        self.cache.update(data)
        self.cache_time = time.time()
        
        return self.cache.get(full_code)
    
    def quick_analyze(self, code, name, market='sh'):
        """快速分析一只股票"""
        s = self.get_stock(code, market)
        if not s:
            return None
        
        change = s['change_pct']
        trend = "🟢涨" if change > 0 else "🔴跌" if change < 0 else "⚪平"
        
        # 技术信号
        if change > 2:
            signal = "强势上涨"
        elif change > 0:
            signal = "温和上涨"
        elif change > -2:
            signal = "震荡整理"
        else:
            signal = "弱势下跌"
        
        return {
            'name': name,
            'code': code,
            'trend': trend,
            'price': s['current'],
            'change': change,
            'signal': signal,
            'amount': s['amount']
        }

# 全局实例
analyzer = AStockAnalyzer()

if __name__ == '__main__':
    # 测试
    result = analyzer.quick_analyze('300059', '东方财富', 'sz')
    print(json.dumps(result, ensure_ascii=False, indent=2))
