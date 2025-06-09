#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理模块
提供简单的配置文件验证功能
"""

import os
import secrets
from typing import Dict, Any


class ConfigManager:
    """简化的配置管理器"""

    DEFAULT_ENV_FILE = '.env'
    
    @classmethod
    def check_config_exists(cls) -> bool:
        """检查配置文件是否存在"""
        return os.path.exists(cls.DEFAULT_ENV_FILE)

    @classmethod
    def generate_secret_key(cls) -> str:
        """生成安全密钥"""
        return secrets.token_urlsafe(32)
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """
        验证配置

        Returns:
            Dict: 验证结果
        """
        result = {
            'valid': True,
            'warnings': [],
            'errors': []
        }

        if not cls.check_config_exists():
            result['valid'] = False
            result['errors'].append('配置文件 .env 不存在，请复制 .env.example 为 .env')
            return result

        try:
            # 检查必要的环境变量
            from config import Config

            # 检查 API Key
            if not Config.GEMINI_API_KEY or Config.GEMINI_API_KEY == 'your_gemini_api_key_here':
                result['warnings'].append('Gemini API Key 未配置，AI 功能将不可用')

            # 检查密钥
            if Config.SECRET_KEY == 'your_secret_key_here':
                result['warnings'].append('建议配置 SECRET_KEY')

            # 检查生产环境配置
            if Config.FLASK_ENV == 'production':
                if Config.DEBUG:
                    result['warnings'].append('生产环境建议关闭 DEBUG 模式')

                if Config.CORS_ORIGINS == ['*']:
                    result['warnings'].append('生产环境建议配置具体的 CORS_ORIGINS')

        except Exception as e:
            result['valid'] = False
            result['errors'].append(f'配置文件格式错误: {str(e)}')

        return result
    

    
    @classmethod
    def get_config_summary(cls) -> Dict[str, Any]:
        """获取配置摘要"""
        if not cls.check_config_exists():
            return {'error': '配置文件 .env 不存在，请复制 .env.example 为 .env'}

        try:
            from config import Config

            return {
                'environment': Config.FLASK_ENV,
                'debug': Config.DEBUG,
                'host': Config.HOST,
                'port': Config.PORT,
                'api_key_configured': bool(
                    Config.GEMINI_API_KEY and
                    Config.GEMINI_API_KEY != 'your_gemini_api_key_here'
                ),
                'secret_key_configured': bool(
                    Config.SECRET_KEY and
                    Config.SECRET_KEY != 'your_secret_key_here'
                )
            }

        except Exception as e:
            return {'error': f'读取配置失败: {str(e)}'}


def main():
    """命令行工具"""
    import sys

    if len(sys.argv) < 2:
        print("用法: python config_manager.py <command>")
        print("命令:")
        print("  validate     - 验证配置")
        print("  summary      - 显示配置摘要")
        print("  generate-key - 生成安全密钥")
        print("  reload       - 重新加载配置")
        print("")
        print("首次使用:")
        print("  1. cp .env.example .env")
        print("  2. 编辑 .env 文件，配置 GEMINI_API_KEY")
        print("  3. python config_manager.py validate")
        return

    command = sys.argv[1]

    if command == 'validate':
        result = ConfigManager.validate_config()
        if result['valid']:
            print("✅ 配置验证通过")
        else:
            print("❌ 配置验证失败")

        for warning in result['warnings']:
            print(f"⚠️  {warning}")

        for error in result['errors']:
            print(f"❌ {error}")

    elif command == 'summary':
        summary = ConfigManager.get_config_summary()
        if 'error' in summary:
            print(f"❌ {summary['error']}")
        else:
            print("📋 配置摘要:")
            for key, value in summary.items():
                print(f"  {key}: {value}")

    elif command == 'generate-key':
        key = ConfigManager.generate_secret_key()
        print(f"生成的安全密钥: {key}")
        print("请将此密钥复制到 .env 文件的 SECRET_KEY 配置项中")

    elif command == 'reload':
        try:
            from config import Config
            Config.reload()
            print("✅ 配置重载成功")

            # 显示重载后的配置摘要
            summary = ConfigManager.get_config_summary()
            if 'error' not in summary:
                print("\n📋 重载后的配置摘要:")
                for key, value in summary.items():
                    print(f"  {key}: {value}")
        except Exception as e:
            print(f"❌ 配置重载失败: {str(e)}")

    else:
        print(f"❌ 未知命令: {command}")
        print("运行 'python config_manager.py' 查看可用命令")


if __name__ == '__main__':
    main()
