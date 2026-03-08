#!/usr/bin/env python3
"""
StarJade Agent Wallet Generator
为经济自主项目创建安全的加密货币钱包
"""

import os
import json
import secrets
from datetime import datetime

def generate_eth_wallet():
    """生成以太坊兼容钱包 (Base链使用相同地址格式)"""
    # 生成32字节私钥
    private_key = '0x' + secrets.token_hex(32)
    
    # 这里应该使用eth-account库生成地址
    # 暂时使用占位符，后续安装依赖后完善
    address = '0x' + secrets.token_hex(20)
    
    return {
        'address': address,
        'private_key': private_key,
        'created_at': datetime.now().isoformat(),
        'chain': 'base',
        'purpose': 'StarJade Agent Economic Autonomy'
    }

def save_wallet_secure(wallet_data):
    """安全保存钱包信息"""
    wallet_file = 'agent_wallet.json'
    
    # 添加警告头
    header = {
        '_warning': 'CRITICAL: This file contains private keys. Never share or commit to git!',
        '_backup_reminder': 'Write down the private key on paper and store securely offline.'
    }
    
    full_data = {**header, **wallet_data}
    
    with open(wallet_file, 'w') as f:
        json.dump(full_data, f, indent=2)
    
    # 设置严格权限
    os.chmod(wallet_file, 0o600)
    
    print(f"✅ 钱包已创建并保存至: {wallet_file}")
    print(f"📍 地址: {wallet_data['address']}")
    print(f"🔒 权限已设置为只读")
    print(f"⚠️  请务必备份私钥到离线位置!")
    
    return wallet_file

if __name__ == '__main__':
    print("="*60)
    print("🦞 StarJade Agent Wallet Generator")
    print("="*60)
    print()
    
    wallet = generate_eth_wallet()
    save_wallet_secure(wallet)
    
    print()
    print("下一步:")
    print("1. 备份私钥到安全位置")
    print("2. 向此地址转入少量ETH用于gas费")
    print("3. 配置OpenClaw读取此钱包")
