#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能 Shell 助手 - 主程序入口
使用大模型将自然语言转换为Shell命令并执行
"""

import sys
import argparse
from typing import Optional
from command_executor import CommandExecutor
from llm_interface import LLMInterface
from history_manager import HistoryManager
from config import Config


class SmartShellAssistant:
    """智能 Shell 助手主类"""

    def __init__(self, config: Config):
        self.config = config
        self.llm = LLMInterface(config)
        self.executor = CommandExecutor(config)
        self.history = HistoryManager(config)

    def process_natural_language(self, user_input: str) -> dict:
        """
        处理用户的自然语言输入

        Args:
            user_input: 用户输入的自然语言

        Returns:
            dict: 包含命令、解释等信息的字典
        """
        # 获取历史上下文
        context = self.history.get_recent_context(limit=5)

        # 调用大模型获取Shell命令
        llm_response = self.llm.natural_language_to_command(
            user_input=user_input,
            context=context,
            system_info=self.executor.get_system_info()
        )

        return llm_response

    def execute_command(self, command: str, auto_execute: bool = False) -> dict:
        """
        执行Shell命令

        Args:
            command: 要执行的Shell命令
            auto_execute: 是否自动执行（不询问用户）

        Returns:
            dict: 执行结果
        """
        if not auto_execute:
            confirm = input(f"\n即将执行命令: {command}\n是否执行? (y/n): ").strip().lower()
            if confirm != 'y':
                return {"status": "cancelled", "message": "用户取消执行"}

        result = self.executor.execute(command)

        # 保存到历史记录
        self.history.add_record(
            user_input=command,
            command=command,
            result=result
        )

        return result

    def interactive_mode(self):
        """交互式模式"""
        print("=" * 60)
        print("智能 Shell 助手 - 交互式模式")
        print("=" * 60)
        print("输入自然语言描述，我会帮你生成并执行Shell命令")
        print("特殊命令:")
        print("  exit/quit - 退出程序")
        print("  history   - 查看历史记录")
        print("  clear     - 清空屏幕")
        print("=" * 60)
        print()

        while True:
            try:
                user_input = input("请输入 > ").strip()

                if not user_input:
                    continue

                # 处理特殊命令
                if user_input.lower() in ['exit', 'quit']:
                    print("再见！")
                    break

                if user_input.lower() == 'history':
                    self.show_history()
                    continue

                if user_input.lower() == 'clear':
                    import os
                    os.system('cls' if sys.platform == 'win32' else 'clear')
                    continue

                # 处理自然语言输入
                print(f"\n正在分析: {user_input}")
                llm_response = self.process_natural_language(user_input)

                if llm_response.get('error'):
                    print(f"错误: {llm_response['error']}")
                    continue

                # 显示生成的命令
                command = llm_response.get('command', '')
                explanation = llm_response.get('explanation', '')
                warnings = llm_response.get('warnings', [])

                print(f"\n建议命令: {command}")
                if explanation:
                    print(f"解释: {explanation}")
                if warnings:
                    print(f"警告: {', '.join(warnings)}")

                # 执行命令
                result = self.execute_command(command, auto_execute=False)

                if result['status'] == 'success':
                    print(f"\n执行成功:")
                    print(result['output'])
                elif result['status'] == 'error':
                    print(f"\n执行失败:")
                    print(result['error'])
                elif result['status'] == 'cancelled':
                    print(f"\n{result['message']}")

                print()

            except KeyboardInterrupt:
                print("\n\n再见！")
                break
            except Exception as e:
                print(f"\n发生错误: {str(e)}")
                if self.config.debug:
                    import traceback
                    traceback.print_exc()

    def single_command_mode(self, user_input: str, auto_execute: bool = False):
        """单命令模式"""
        print(f"正在分析: {user_input}")
        llm_response = self.process_natural_language(user_input)

        if llm_response.get('error'):
            print(f"错误: {llm_response['error']}")
            return

        command = llm_response.get('command', '')
        explanation = llm_response.get('explanation', '')

        print(f"\n建议命令: {command}")
        if explanation:
            print(f"解释: {explanation}")

        if auto_execute:
            result = self.execute_command(command, auto_execute=True)
            if result['status'] == 'success':
                print(f"\n执行成功:")
                print(result['output'])
            elif result['status'] == 'error':
                print(f"\n执行失败:")
                print(result['error'])

    def show_history(self, limit: int = 10):
        """显示历史记录"""
        records = self.history.get_recent_context(limit=limit)

        if not records:
            print("暂无历史记录")
            return

        print(f"\n最近 {len(records)} 条历史记录:")
        print("-" * 60)
        for i, record in enumerate(records, 1):
            print(f"{i}. 输入: {record.get('user_input', 'N/A')}")
            print(f"   命令: {record.get('command', 'N/A')}")
            print(f"   状态: {record.get('status', 'N/A')}")
            print("-" * 60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='智能 Shell 助手 - 使用大模型将自然语言转换为Shell命令'
    )
    parser.add_argument(
        'input',
        nargs='*',
        help='自然语言输入（不提供则进入交互模式）'
    )
    parser.add_argument(
        '-y', '--yes',
        action='store_true',
        help='自动执行命令，不询问确认'
    )
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='开启调试模式'
    )
    parser.add_argument(
        '--history',
        action='store_true',
        help='显示历史记录'
    )

    args = parser.parse_args()

    # 加载配置
    config = Config(debug=args.debug)

    # 创建助手实例
    assistant = SmartShellAssistant(config)

    # 根据参数选择模式
    if args.history:
        assistant.show_history()
    elif args.input:
        user_input = ' '.join(args.input)
        assistant.single_command_mode(user_input, auto_execute=args.yes)
    else:
        assistant.interactive_mode()


if __name__ == '__main__':
    main()
