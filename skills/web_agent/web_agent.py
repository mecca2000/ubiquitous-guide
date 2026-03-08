#!/usr/bin/env python3
"""
StarJade Web Agent - 高速外网连接模块
用于Moltbook API、股票数据等轻量级请求
"""

import requests
import json
import time
from typing import Optional, Dict, Any
from urllib.parse import urljoin

class WebAgent:
    """轻量级Web代理 - 速度快、效果好"""
    
    def __init__(self, timeout: int = 10, retries: int = 2):
        self.timeout = timeout
        self.retries = retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'StarJade-Agent/1.0 (Python Requests)',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
        self._last_response_time = 0
    
    def get(self, url: str, headers: Optional[Dict] = None, 
            params: Optional[Dict] = None) -> Dict[str, Any]:
        """GET请求 - 极速版"""
        start = time.time()
        
        for attempt in range(self.retries):
            try:
                response = self.session.get(
                    url, 
                    headers=headers,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                self._last_response_time = time.time() - start
                
                # 尝试JSON解析
                try:
                    return {
                        'success': True,
                        'data': response.json(),
                        'status': response.status_code,
                        'time_ms': round(self._last_response_time * 1000, 2)
                    }
                except:
                    return {
                        'success': True,
                        'text': response.text,
                        'status': response.status_code,
                        'time_ms': round(self._last_response_time * 1000, 2)
                    }
                    
            except requests.exceptions.Timeout:
                if attempt == self.retries - 1:
                    return {'success': False, 'error': 'Timeout', 'time_ms': round((time.time() - start) * 1000, 2)}
                time.sleep(0.5)
            except Exception as e:
                if attempt == self.retries - 1:
                    return {'success': False, 'error': str(e), 'time_ms': round((time.time() - start) * 1000, 2)}
                time.sleep(0.5)
    
    def post(self, url: str, data: Optional[Dict] = None, 
             json_data: Optional[Dict] = None,
             headers: Optional[Dict] = None) -> Dict[str, Any]:
        """POST请求 - 极速版"""
        start = time.time()
        
        for attempt in range(self.retries):
            try:
                response = self.session.post(
                    url,
                    data=data,
                    json=json_data,
                    headers=headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                self._last_response_time = time.time() - start
                
                try:
                    return {
                        'success': True,
                        'data': response.json(),
                        'status': response.status_code,
                        'time_ms': round(self._last_response_time * 1000, 2)
                    }
                except:
                    return {
                        'success': True,
                        'text': response.text,
                        'status': response.status_code,
                        'time_ms': round(self._last_response_time * 1000, 2)
                    }
                    
            except requests.exceptions.Timeout:
                if attempt == self.retries - 1:
                    return {'success': False, 'error': 'Timeout', 'time_ms': round((time.time() - start) * 1000, 2)}
                time.sleep(0.5)
            except Exception as e:
                if attempt == self.retries - 1:
                    return {'success': False, 'error': str(e), 'time_ms': round((time.time() - start) * 1000, 2)}
                time.sleep(0.5)
    
    def moltbook_get(self, endpoint: str, token: Optional[str] = None) -> Dict[str, Any]:
        """Moltbook专用GET请求"""
        base_url = "https://api.moltbook.com/v1"
        url = urljoin(base_url, endpoint)
        
        headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        return self.get(url, headers=headers)
    
    def moltbook_post(self, endpoint: str, data: Dict, 
                      token: Optional[str] = None) -> Dict[str, Any]:
        """Moltbook专用POST请求"""
        base_url = "https://api.moltbook.com/v1"
        url = urljoin(base_url, endpoint)
        
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        return self.post(url, json_data=data, headers=headers)
    
    def stock_quote(self, symbol: str) -> Dict[str, Any]:
        """获取股票实时行情（新浪财经）"""
        url = f"https://hq.sinajs.cn/list={symbol}"
        headers = {'Referer': 'https://finance.sina.com.cn'}
        
        result = self.get(url, headers=headers)
        if result['success'] and 'text' in result:
            # 解析新浪返回的JS格式数据
            text = result['text']
            try:
                # 提取var hq_str_xxx="..."中的内容
                import re
                match = re.search(r'"([^"]*)"', text)
                if match:
                    data = match.group(1).split(',')
                    return {
                        'success': True,
                        'symbol': symbol,
                        'name': data[0],
                        'price': float(data[3]),
                        'change': float(data[3]) - float(data[2]),
                        'change_pct': round((float(data[3]) - float(data[2])) / float(data[2]) * 100, 2),
                        'volume': int(data[8]),
                        'time_ms': result['time_ms']
                    }
            except:
                pass
        return result

# 便捷函数
def fetch(url: str, **kwargs) -> Dict[str, Any]:
    """快速获取URL内容"""
    agent = WebAgent()
    return agent.get(url, **kwargs)

def moltbook(endpoint: str, method: str = 'get', **kwargs) -> Dict[str, Any]:
    """快速调用Moltbook API"""
    agent = WebAgent()
    if method.lower() == 'post':
        return agent.moltbook_post(endpoint, **kwargs)
    return agent.moltbook_get(endpoint, **kwargs)

if __name__ == '__main__':
    # 测试
    print("🚀 WebAgent 测试")
    print("-" * 40)
    
    agent = WebAgent()
    
    # 测试普通GET
    print("\n1. 测试百度首页...")
    result = agent.get('https://www.baidu.com')
    print(f"   状态: {'✅' if result['success'] else '❌'}")
    print(f"   耗时: {result['time_ms']}ms")
    
    # 测试股票API
    print("\n2. 测试股票行情(东方财富)...")
    result = agent.stock_quote('sz300059')
    if result['success'] and 'price' in result:
        print(f"   名称: {result['name']}")
        print(f"   价格: ¥{result['price']}")
        print(f"   涨跌: {result['change_pct']}%")
        print(f"   耗时: {result['time_ms']}ms")
    else:
        print(f"   结果: {result}")
    
    print("\n✅ 测试完成!")
