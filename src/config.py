#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
管理应用程序的配置项
"""

import os
import json
from typing import Optional


class Config:
    """配置类"""

    def __init__(self, config_file: Optional[str] = None, debug: bool = False):
        """
        初始化配置

        Args:
            config_file: 配置文件路径（可选）
            debug: 是否开启调试模式
        """
        # 基础配置
        self.debug = debug
        self.config_file = config_file or 'config.json'

        # LLM 相关配置
        self.api_key = os.environ.get('OPENAI_API_KEY', '')  # 从环境变量读取
        self.api_base = os.environ.get('OPENAI_API_BASE', 'https://api.openai.com/v1')
        self.model_name = 'gpt-4'  # 默认模型
        self.temperature = 0.3  # 温度参数，越低越确定
        self.max_tokens = 1000  # 最大token数

        # 命令执行配置
        self.command_timeout = 30  # 命令执行超时时间（秒）
        self.auto_confirm = False  # 是否自动确认执行命令

        # 历史记录配置
        self.history_file = 'shell_history.json'
        self.max_history_records = 100  # 最大历史记录数

        # 安全配置
        self.enable_dangerous_command_check = True  # 是否启用危险命令检查
        self.allow_destructive_commands = False  # 是否允许破坏性命令

        # UI配置
        self.show_warnings = True  # 是否显示警告信息
        self.color_output = True  # 是否启用彩色输出

        # 从配置文件加载（如果存在）
        self._load_config()

    def _load_config(self):
        """从配置文件加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self._update_from_dict(config_data)
                if self.debug:
                    print(f"✅ 已加载配置文件: {self.config_file}")
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  警告: 无法加载配置文件 {self.config_file}: {e}")
        else:
            if self.debug:
                print(f"ℹ️  配置文件不存在，使用默认配置: {self.config_file}")

    def _update_from_dict(self, config_data: dict):
        """从字典更新配置"""
        for key, value in config_data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def save_config(self):
        """保存配置到文件"""
        config_data = {
            'model_name': self.model_name,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'command_timeout': self.command_timeout,
            'auto_confirm': self.auto_confirm,
            'max_history_records': self.max_history_records,
            'enable_dangerous_command_check': self.enable_dangerous_command_check,
            'allow_destructive_commands': self.allow_destructive_commands,
            'show_warnings': self.show_warnings,
            'color_output': self.color_output,
            # 注意: 不保存 api_key 到文件，保持在环境变量中更安全
        }

        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            print(f"✅ 配置已保存到: {self.config_file}")
        except IOError as e:
            print(f"❌ 保存配置失败: {e}")

    def validate(self) -> tuple[bool, Optional[str]]:
        """
        验证配置是否有效

        Returns:
            tuple: (是否有效, 错误信息)
        """
        # 检查 API Key
        if not self.api_key:
            return False, "API Key 未设置。请设置环境变量 OPENAI_API_KEY"

        # 检查其他配置
        if self.command_timeout <= 0:
            return False, "command_timeout 必须大于 0"

        if self.max_history_records < 0:
            return False, "max_history_records 不能为负数"

        return True, None

    def print_config(self):
        """打印当前配置"""
        print("=" * 60)
        print("当前配置:")
        print("=" * 60)
        print(f"调试模式: {self.debug}")
        print(f"模型名称: {self.model_name}")
        print(f"温度参数: {self.temperature}")
        print(f"最大Token: {self.max_tokens}")
        print(f"API Base: {self.api_base}")
        print(f"API Key: {'已设置' if self.api_key else '未设置'}")
        print(f"命令超时: {self.command_timeout}秒")
        print(f"自动确认: {self.auto_confirm}")
        print(f"历史记录文件: {self.history_file}")
        print(f"最大历史记录数: {self.max_history_records}")
        print(f"危险命令检查: {self.enable_dangerous_command_check}")
        print(f"允许破坏性命令: {self.allow_destructive_commands}")
        print("=" * 60)


def create_default_config():
    """创建默认配置文件"""
    config = Config()
    config.save_config()
    print("✅ 已创建默认配置文件")


if __name__ == '__main__':
    # 测试配置
    config = Config(debug=True)
    config.print_config()

    # 验证配置
    valid, error = config.validate()
    if valid:
        print("\n✅ 配置验证通过")
    else:
        print(f"\n❌ 配置验证失败: {error}")
