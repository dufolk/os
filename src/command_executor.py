#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令执行模块
负责安全地执行Shell命令并返回结果
"""

import subprocess
import sys
import platform
import os
from typing import Dict, Optional


class CommandExecutor:
    """Shell命令执行器"""

    def __init__(self, config):
        """
        初始化命令执行器

        Args:
            config: 配置对象
        """
        self.config = config
        self.platform = platform.system()
        self.timeout = config.command_timeout if hasattr(config, 'command_timeout') else 30

    def execute(self, command: str, timeout: Optional[int] = None) -> Dict:
        """
        执行Shell命令

        Args:
            command: 要执行的Shell命令
            timeout: 超时时间（秒），None则使用默认值

        Returns:
            Dict: 执行结果，格式:
                  {
                      'status': 'success'/'error',
                      'output': '标准输出',
                      'error': '错误输出',
                      'return_code': 0,
                      'command': '执行的命令'
                  }
        """
        if not command or not command.strip():
            return {
                'status': 'error',
                'output': '',
                'error': '命令不能为空',
                'return_code': -1,
                'command': command
            }

        # 使用配置的超时时间
        exec_timeout = timeout if timeout is not None else self.timeout

        try:
            # 根据操作系统选择Shell
            if self.platform == 'Windows':
                shell_cmd = command
                use_shell = True
            else:
                shell_cmd = command
                use_shell = True

            # 执行命令
            process = subprocess.Popen(
                shell_cmd,
                shell=use_shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            # 等待命令完成
            stdout, stderr = process.communicate(timeout=exec_timeout)
            return_code = process.returncode

            # 判断执行状态
            if return_code == 0:
                status = 'success'
            else:
                status = 'error'

            return {
                'status': status,
                'output': stdout.strip() if stdout else '',
                'error': stderr.strip() if stderr else '',
                'return_code': return_code,
                'command': command
            }

        except subprocess.TimeoutExpired:
            process.kill()
            return {
                'status': 'error',
                'output': '',
                'error': f'命令执行超时（{exec_timeout}秒）',
                'return_code': -1,
                'command': command
            }

        except FileNotFoundError as e:
            return {
                'status': 'error',
                'output': '',
                'error': f'命令未找到: {str(e)}',
                'return_code': -1,
                'command': command
            }

        except PermissionError as e:
            return {
                'status': 'error',
                'output': '',
                'error': f'权限不足: {str(e)}',
                'return_code': -1,
                'command': command
            }

        except Exception as e:
            return {
                'status': 'error',
                'output': '',
                'error': f'执行失败: {str(e)}',
                'return_code': -1,
                'command': command
            }

    def get_system_info(self) -> Dict:
        """
        获取系统信息

        Returns:
            Dict: 系统信息字典
        """
        info = {
            'platform': self.platform,
            'version': platform.version(),
            'current_dir': os.getcwd(),
            'shell': self._get_shell_type(),
            'python_version': platform.python_version(),
            'architecture': platform.machine()
        }

        return info

    def _get_shell_type(self) -> str:
        """
        获取当前使用的Shell类型

        Returns:
            str: Shell类型（如 cmd, powershell, bash, zsh等）
        """
        if self.platform == 'Windows':
            # Windows上检查是否在PowerShell中
            if os.environ.get('PSModulePath'):
                return 'PowerShell'
            else:
                return 'cmd'
        else:
            # Unix-like系统
            shell = os.environ.get('SHELL', '')
            if 'bash' in shell:
                return 'bash'
            elif 'zsh' in shell:
                return 'zsh'
            elif 'fish' in shell:
                return 'fish'
            else:
                return 'sh'

    def is_dangerous_command(self, command: str) -> tuple[bool, Optional[str]]:
        """
        检查命令是否危险

        Args:
            command: 要检查的命令

        Returns:
            tuple: (是否危险, 警告信息)
        """
        dangerous_patterns = {
            'rm -rf /': '删除根目录，极度危险！',
            'rm -rf /*': '删除根目录下所有文件，极度危险！',
            'mkfs': '格式化磁盘，会丢失所有数据！',
            'dd if=': '直接操作设备，可能损坏系统！',
            ':(){ :|:& };:': 'Fork炸弹，会导致系统崩溃！',
            'chmod -R 777': '修改所有文件权限，严重安全隐患！',
            'chown -R': '修改文件所有者，可能导致权限问题！'
        }

        command_lower = command.lower().strip()

        for pattern, warning in dangerous_patterns.items():
            if pattern.lower() in command_lower:
                return True, warning

        # 检查删除操作
        if 'rm ' in command_lower and '-rf' in command_lower:
            return True, '强制递归删除操作，请谨慎！'

        # 检查格式化操作
        if self.platform == 'Windows' and 'format' in command_lower:
            return True, '格式化操作，会丢失数据！'

        return False, None

    def validate_command_syntax(self, command: str) -> tuple[bool, Optional[str]]:
        """
        验证命令语法（基础检查）

        Args:
            command: 要验证的命令

        Returns:
            tuple: (是否有效, 错误信息)
        """
        if not command or not command.strip():
            return False, "命令不能为空"

        # 检查是否包含非法字符
        # 注意: 这是一个简单的检查，可能需要根据实际情况调整
        if command.count('"') % 2 != 0 or command.count("'") % 2 != 0:
            return False, "引号不匹配"

        return True, None


# ===== 辅助函数 =====

def test_executor():
    """测试命令执行器"""
    from config import Config

    config = Config()
    executor = CommandExecutor(config)

    # 获取系统信息
    print("系统信息:")
    info = executor.get_system_info()
    for key, value in info.items():
        print(f"  {key}: {value}")

    # 测试简单命令
    print("\n测试命令执行:")
    if platform.system() == 'Windows':
        test_command = 'echo Hello World'
    else:
        test_command = 'echo "Hello World"'

    result = executor.execute(test_command)
    print(f"  命令: {result['command']}")
    print(f"  状态: {result['status']}")
    print(f"  输出: {result['output']}")


if __name__ == '__main__':
    test_executor()
