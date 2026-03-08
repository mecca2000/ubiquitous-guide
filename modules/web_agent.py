#!/usr/bin/env python3
"""
Web Agent - 轻量级外网访问代理
高速、无AI、预配置规则
"""

import requests
import json
import time
from datetime import datetime

class WebAgent:
    """精简外网代理"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.cache = {}
    
    # ========== Moltbook API ==========
    def moltbook_feed(self, limit=10):
        """获取Moltbook热门帖子"""
        url = "https://www.moltbook.com/api/v1/posts"
        headers = {'Authorization': 'Bearer molt_sk_7f8a9b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0'}
        try:
            r = self.session.get(url, headers=headers, params={'sort': 'hot', 'limit': limit}, timeout=5)
            return r.json() if r.status_code == 200 else None
        except:
            return None
    
    def moltbook_search(self, query, limit=5):
        """搜索Moltbook帖子"""
        url = "https://www.moltbook.com/api/v1/search"
        headers = {'Authorization': 'Bearer molt_sk_7f8a9b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0'}
        try:
            r = self.session.get(url, headers=headers, params={'q': query, 'type': 'posts', 'limit': limit}, timeout=5)
            return r.json() if r.status_code == 200 else None
        except:
            return None
    
    # ========== 股票数据 ==========
    def stock_realtime(self, codes):
        """获取A股实时行情 codes: ['sh600309', 'sz300059']"""
        url = f"https://hq.sinajs.cn/list={','.join(codes)}"
        headers = {'Referer': 'https://finance.sina.com.cn'}
        try:
            r = self.session.get(url, headers=headers, timeout=3)
            r.encoding = 'gb2312'
            return self._parse_sina(r.text)
        except:
            return {}
    
    def _parse_sina(self, text):
        """解析新浪数据"""
        result = {}
        for line in text.strip().split('\n'):
            if '=' in line and 'var hq_str_' in line:
                parts = line.split('=')
                code = parts[0].replace('var hq_str_', '')
                data = parts[1].strip().strip('";').split(',')
                if len(data) >= 33:
                    result[code] = {
                        'name': data[0],
                        'price': float(data[3]),
                        'prev': float(data[2]),
                        'change': ((float(data[3]) - float(data[2])) / float(data[2])) * 100
                    }
        return result
    
    # ========== 自动任务 ==========
    def auto_check_moltbook(self, keywords=None):
        """自动检查Moltbook关键词"""
        feed = self.moltbook_feed(20)
        if not feed or not feed.get('success'):
            return []
        
        matches = []
        keywords = keywords or ['economic', 'autonomy', 'crypto', 'skill']
        
        for post in feed.get('posts', []):
            content = (post.get('title', '') + ' ' + post.get('content', '')).lower()
            for kw in keywords:
                if kw in content:
                    matches.append({
                        'id': post['id'],
                        'title': post['title'],
                        'author': post.get('author', {}).get('name'),
                        'keyword': kw
                    })
                    break
        return matches

# 全局实例
web = WebAgent()

if __name__ == '__main__':
    # 测试
    print("Testing Web Agent...")
    stocks = web.stock_realtime(['sh600309', 'sz300059'])
    for code, data in stocks.items():
        print(f"{code}: {data['name']} ¥{data['price']} ({data['change']:+.2f}%)")
