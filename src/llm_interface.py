#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM 接口模块
这个文件需要你来完成大模型调用的具体实现
"""

from typing import Dict, List, Optional


class LLMInterface:
    """大模型接口类"""

    def __init__(self, config):
        """
        初始化 LLM 接口

        Args:
            config: 配置对象
        """
        self.config = config
        # TODO: 在这里初始化你的大模型客户端
        # 例如: self.client = OpenAI(api_key=config.api_key)
        pass

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

        # ===== 以下是示例代码，你需要替换成真实的大模型调用 =====

        # 示例: 构建系统提示词
        system_prompt = self._build_system_prompt(system_info)

        # 示例: 构建用户提示词（包含上下文）
        user_prompt = self._build_user_prompt(user_input, context)

        # TODO: 调用你的大模型 API
        # 例如:
        # response = self.client.chat.completions.create(
        #     model="gpt-4",
        #     messages=[
        #         {"role": "system", "content": system_prompt},
        #         {"role": "user", "content": user_prompt}
        #     ]
        # )
        #
        # command_text = response.choices[0].message.content

        # 临时返回示例（你需要替换）
        return {
            'command': 'echo "请在 llm_interface.py 中实现大模型调用"',
            'explanation': '这是一个占位符命令，请完成 natural_language_to_command 函数',
            'warnings': ['LLM接口尚未实现'],
            'error': None
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

        prompt = f"""你是一个专业的 Shell 命令助手。你的任务是将用户的自然语言描述转换为准确的Shell命令。

当前系统信息:
- 操作系统: {platform}
- Shell: {system_info.get('shell', 'unknown') if system_info else 'unknown'}
- 当前目录: {system_info.get('current_dir', 'unknown') if system_info else 'unknown'}

请遵循以下规则:
1. 只返回命令本身，不要有多余的解释文字在命令中
2. 确保命令在 {platform} 系统上可以执行
3. 如果任务不明确，返回最常用的命令
4. 如果命令可能有危险（如删除文件），请在 warnings 中说明
5. 返回格式必须是 JSON:
   {{
       "command": "实际的shell命令",
       "explanation": "命令的中文解释",
       "warnings": ["警告信息列表（可选）"]
   }}

示例:
用户: "显示当前目录下的所有文件"
返回: {{"command": "ls -la", "explanation": "列出当前目录下所有文件（包括隐藏文件）的详细信息", "warnings": []}}
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
