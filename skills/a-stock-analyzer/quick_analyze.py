#!/usr/bin/env python3
"""
A股极速分析 - 命令行入口
用法: python quick_analyze.py 300059 东方财富 sz
"""

import sys
sys.path.insert(0, '/home/admin/.openclaw/workspace/skills/a-stock-analyzer')

from analyzer import analyzer

def main():
    if len(sys.argv) < 3:
        # 默认分析常用股票
        stocks = [
            ('300059', '东方财富', 'sz'),
            ('300803', '指南针', 'sz'),
            ('600309', '万华化学', 'sh'),
            ('002463', '沪电股份', 'sz'),
            ('000001', '上证指数', 'sh')
        ]
    else:
        code = sys.argv[1]
        name = sys.argv[2]
        market = sys.argv[3] if len(sys.argv) > 3 else 'sh'
        stocks = [(code, name, market)]
    
    print("=" * 60)
    print("📊 A股极速分析")
    print("=" * 60)
    
    for code, name, market in stocks:
        result = analyzer.quick_analyze(code, name, market)
        if result:
            print(f"\n{result['trend']} {result['name']}({result['code']})")
            print(f"   ¥{result['price']:.2f} ({result['change']:+.2f}%)")
            print(f"   {result['signal']} | 成交{result['amount']:.1f}亿")
        else:
            print(f"\n⚠️ {name}: 获取失败")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
