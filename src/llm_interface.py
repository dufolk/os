#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM 接口模块
使用通义千问（Qwen）大模型
"""

from typing import Dict, List, Optional
import dashscope
import json


class LLMInterface:
    """大模型接口类"""

    def __init__(self, config):
        """
        初始化 LLM 接口

        Args:
            config: 配置对象
        """
        self.config = config
        # 设置通义千问 API Key
        dashscope.api_key = config.api_key
        # 设置模型名称（可以在 config 中配置）
        self.model_name = getattr(config, 'model_name', 'qwen-turbo')

    def natural_language_to_command(
        self,
        user_input: str,
        context: List[Dict] = None,
        system_info: Dict = None
    ) -> Dict:
        """
        将自然语言转换为Shell命令

        这是核心接口函数，需要你来实现！

        Args:
            user_input: 用户输入的自然语言描述
            context: 历史上下文记录列表，每条记录包含:
                     {
                         'user_input': '用户输入',
                         'command': '执行的命令',
                         'status': '执行状态',
                         'output': '命令输出'
                     }
            system_info: 系统信息，包含:
                        {
                            'platform': 'Windows/Linux/Darwin',
                            'version': '系统版本',
                            'current_dir': '当前工作目录',
                            'shell': '当前使用的Shell'
                        }

        Returns:
            Dict: 返回字典格式:
                  {
                      'command': 'ls -la',           # 生成的Shell命令
                      'explanation': '列出当前目录所有文件',  # 命令解释
                      'warnings': ['该命令会显示隐藏文件'],   # 可选的警告信息
                      'error': None                   # 如果出错，这里包含错误信息
                  }

        示例实现思路:
            1. 构建 prompt，包含:
               - 系统角色: "你是一个Shell命令专家..."
               - 用户输入
               - 系统信息 (Windows/Linux等)
               - 历史上下文
            2. 调用大模型 API
            3. 解析返回结果，提取命令和解释
            4. 返回标准格式的字典

        TODO: 请实现这个函数！
        """

        try:
            # 构建系统提示词
            system_prompt = self._build_system_prompt(system_info)

            # 构建用户提示词（包含上下文）
            user_prompt = self._build_user_prompt(user_input, context)

            # 调用通义千问 API
            response = dashscope.Generation.call(
                model=self.model_name,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                result_format='message',  # 设置返回格式
                temperature=0.3,  # 降低随机性，使输出更确定
            )

            # 检查响应状态
            if response.status_code == 200:
                # 提取返回内容
                result_text = response.output.choices[0].message.content
                
                # 解析 JSON 响应
                result = parse_llm_json_response(result_text)
                
                # 确保返回格式正确
                if 'command' not in result:
                    return {
                        'command': 'echo "LLM 未返回有效命令"',
                        'explanation': '大模型返回格式错误',
                        'warnings': ['返回格式不正确'],
                        'error': 'Invalid response format'
                    }
                
                # 添加 error 字段（如果不存在）
                if 'error' not in result:
                    result['error'] = None
                
                # 确保 warnings 字段存在
                if 'warnings' not in result:
                    result['warnings'] = []
                
                return result
            else:
                # API 调用失败
                error_msg = f"API 调用失败: {response.code} - {response.message}"
                return {
                    'command': 'echo "API 调用失败"',
                    'explanation': error_msg,
                    'warnings': [],
                    'error': error_msg
                }

        except Exception as e:
            # 捕获所有异常
            error_msg = f"LLM 调用出错: {str(e)}"
            return {
                'command': 'echo "LLM 调用出错"',
                'explanation': error_msg,
                'warnings': [],
                'error': error_msg
            }

    def _build_system_prompt(self, system_info: Optional[Dict]) -> str:
        """
        构建系统提示词

        Args:
            system_info: 系统信息

        Returns:
            str: 系统提示词
        """
        platform = system_info.get('platform', 'unknown') if system_info else 'unknown'

        shell_type = system_info.get('shell', 'unknown') if system_info else 'unknown'
        
        # 根据 Shell 类型提供不同的示例
        if shell_type == 'PowerShell':
            example_cmd = 'Get-ChildItem'
            example_explanation = '列出当前目录下所有文件和文件夹'
        elif shell_type == 'cmd':
            example_cmd = 'dir'
            example_explanation = '显示当前目录下的文件和文件夹'
        else:
            example_cmd = 'ls -la'
            example_explanation = '列出当前目录下所有文件（包括隐藏文件）的详细信息'
        
        prompt = f"""你是一个专业的 Shell 命令助手。你的任务是将用户的自然语言描述转换为准确的Shell命令。

当前系统信息:
- 操作系统: {platform}
- Shell: {shell_type}
- 当前目录: {system_info.get('current_dir', 'unknown') if system_info else 'unknown'}

请遵循以下规则:
1. 只返回命令本身，不要有多余的解释文字在命令中
2. 确保命令在 {platform} 系统的 {shell_type} 中可以执行
3. 如果是 PowerShell，使用 PowerShell 命令（如 Get-ChildItem, Get-Process 等）
4. 如果是 cmd，使用 CMD 命令（如 dir, tasklist 等）
5. 如果是 bash/zsh，使用 Unix 命令（如 ls, ps 等）
6. 如果任务不明确，返回最常用的命令
7. 如果命令可能有危险（如删除文件），请在 warnings 中说明
8. 返回格式必须是 JSON:
   {{
       "command": "实际的shell命令",
       "explanation": "命令的中文解释",
       "warnings": ["警告信息列表（可选）"]
   }}

示例:
用户: "显示当前目录下的所有文件"
返回: {{"command": "{example_cmd}", "explanation": "{example_explanation}", "warnings": []}}
"""
        return prompt

    def _build_user_prompt(self, user_input: str, context: Optional[List[Dict]]) -> str:
        """
        构建用户提示词，包含历史上下文

        Args:
            user_input: 用户输入
            context: 历史上下文

        Returns:
            str: 用户提示词
        """
        prompt = ""

        # 添加历史上下文
        if context and len(context) > 0:
            prompt += "历史命令记录（供参考）:\n"
            for i, record in enumerate(context[-3:], 1):  # 只取最近3条
                prompt += f"{i}. 用户: {record.get('user_input', '')}\n"
                prompt += f"   命令: {record.get('command', '')}\n"
                if record.get('status') == 'success':
                    prompt += f"   结果: 执行成功\n"
                else:
                    prompt += f"   结果: 执行失败\n"
            prompt += "\n"

        # 添加当前用户输入
        prompt += f"当前需求: {user_input}\n"
        prompt += "请返回JSON格式的命令。"

        return prompt

    def explain_command(self, command: str) -> str:
        """
        解释Shell命令的作用（可选功能）

        Args:
            command: Shell命令

        Returns:
            str: 命令解释

        TODO: 可选实现，用于解释用户输入的命令
        """
        # TODO: 调用大模型解释命令
        return f"命令 '{command}' 的解释功能尚未实现"

    def suggest_fix(self, command: str, error_message: str) -> Dict:
        """
        根据错误信息建议修复方案（可选功能）

        Args:
            command: 执行失败的命令
            error_message: 错误信息

        Returns:
            Dict: 包含修复建议的字典

        TODO: 可选实现，用于命令执行失败后给出修复建议
        """
        # TODO: 调用大模型分析错误并给出修复建议
        return {
            'fixed_command': command,
            'explanation': '错误修复功能尚未实现',
            'error': None
        }


# ===== 以下是一些辅助函数，帮助你实现大模型调用 =====

def parse_llm_json_response(response_text: str) -> Dict:
    """
    解析大模型返回的JSON格式响应

    Args:
        response_text: 大模型返回的文本

    Returns:
        Dict: 解析后的字典
    """
    import json
    import re

    # 尝试提取JSON部分
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    # 如果解析失败，返回默认格式
    return {
        'command': 'echo "解析LLM响应失败"',
        'explanation': '无法解析大模型返回的结果',
        'warnings': ['JSON解析失败'],
        'error': 'Failed to parse LLM response'
    }


def validate_command(command: str, platform: str) -> bool:
    """
    验证命令是否安全（基础检查）

    Args:
        command: 要验证的命令
        platform: 操作系统平台

    Returns:
        bool: 命令是否安全
    """
    # 危险命令列表（可以扩展）
    dangerous_patterns = [
        r'rm\s+-rf\s+/',      # 删除根目录
        r'mkfs',              # 格式化磁盘
        r'dd\s+if=.*of=/dev', # 直接写入设备
        r':\(\)\{.*\}',       # Fork炸弹
    ]

    import re
    for pattern in dangerous_patterns:
        if re.search(pattern, command):
            return False

    return True
