#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试脚本
用于验证框架各个模块是否正常工作
"""

import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def test_config():
    """测试配置模块"""
    print("=" * 60)
    print("测试 1: 配置模块")
    print("=" * 60)
    try:
        from config import Config
        config = Config(debug=True)
        config.print_config()

        valid, error = config.validate()
        if valid:
            print("✅ 配置验证通过")
        else:
            print(f"⚠️  配置验证失败: {error}")
            print("   提示: 请设置环境变量 OPENAI_API_KEY")

        return True
    except Exception as e:
        print(f"❌ 配置模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_command_executor():
    """测试命令执行模块"""
    print("\n" + "=" * 60)
    print("测试 2: 命令执行模块")
    print("=" * 60)
    try:
        from config import Config
        from command_executor import CommandExecutor

        config = Config()
        executor = CommandExecutor(config)

        # 获取系统信息
        print("\n系统信息:")
        info = executor.get_system_info()
        for key, value in info.items():
            print(f"  {key}: {value}")

        # 测试简单命令
        print("\n测试命令执行:")
        import platform
        if platform.system() == 'Windows':
            test_command = 'echo Hello from Smart Shell Assistant'
        else:
            test_command = 'echo "Hello from Smart Shell Assistant"'

        result = executor.execute(test_command)
        print(f"  命令: {result['command']}")
        print(f"  状态: {result['status']}")
        print(f"  输出: {result['output']}")

        if result['status'] == 'success':
            print("✅ 命令执行模块测试通过")
            return True
        else:
            print("❌ 命令执行失败")
            return False

    except Exception as e:
        print(f"❌ 命令执行模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_history_manager():
    """测试历史记录模块"""
    print("\n" + "=" * 60)
    print("测试 3: 历史记录模块")
    print("=" * 60)
    try:
        from config import Config
        from history_manager import HistoryManager

        config = Config()
        history = HistoryManager(config)

        # 添加测试记录
        history.add_record(
            user_input="显示当前目录",
            command="ls -la",
            result={'status': 'success', 'output': 'test output', 'error': '', 'return_code': 0}
        )

        history.add_record(
            user_input="查看文件",
            command="cat test.txt",
            result={'status': 'error', 'output': '', 'error': 'File not found', 'return_code': 1}
        )

        # 获取统计信息
        stats = history.get_statistics()
        print("\n历史记录统计:")
        print(f"  总命令数: {stats['total_commands']}")
        print(f"  成功: {stats['success_count']}")
        print(f"  失败: {stats['error_count']}")
        print(f"  成功率: {stats['success_rate']:.1%}")

        # 显示最近记录
        print("\n最近的记录:")
        for record in history.get_recent_context(2):
            print(f"  - {record['user_input']} -> {record['command']} ({record['status']})")

        print("✅ 历史记录模块测试通过")
        return True

    except Exception as e:
        print(f"❌ 历史记录模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_llm_interface():
    """测试 LLM 接口模块"""
    print("\n" + "=" * 60)
    print("测试 4: LLM 接口模块")
    print("=" * 60)
    try:
        from config import Config
        from llm_interface import LLMInterface

        config = Config()
        llm = LLMInterface(config)

        # 测试接口调用（使用占位符实现）
        result = llm.natural_language_to_command(
            user_input="显示当前目录的所有文件",
            context=[],
            system_info={'platform': 'Windows', 'shell': 'cmd'}
        )

        print("\nLLM 接口返回:")
        print(f"  命令: {result.get('command', 'N/A')}")
        print(f"  解释: {result.get('explanation', 'N/A')}")
        print(f"  警告: {result.get('warnings', [])}")

        if 'command' in result:
            print("✅ LLM 接口模块测试通过（占位符）")
            print("⚠️  注意: 请在 src/llm_interface.py 中完成真实的大模型调用")
            return True
        else:
            print("❌ LLM 接口返回格式错误")
            return False

    except Exception as e:
        print(f"❌ LLM 接口模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("智能 Shell 助手 - 框架测试")
    print("=" * 60)
    print()

    results = []

    # 运行各项测试
    results.append(("配置模块", test_config()))
    results.append(("命令执行模块", test_command_executor()))
    results.append(("历史记录模块", test_history_manager()))
    results.append(("LLM 接口模块", test_llm_interface()))

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name}: {status}")

    all_passed = all(result[1] for result in results)
    print("=" * 60)

    if all_passed:
        print("\n🎉 所有测试通过！框架搭建完成。")
        print("\n下一步:")
        print("  1. 在 src/llm_interface.py 中实现大模型调用")
        print("  2. 设置环境变量 OPENAI_API_KEY（或其他 API Key）")
        print("  3. 运行 python src/main.py 开始使用")
    else:
        print("\n⚠️  部分测试失败，请检查错误信息。")

    print()


if __name__ == '__main__':
    main()
