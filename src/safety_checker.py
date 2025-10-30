#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令安全检查模块
评估命令的风险等级
"""

from typing import Tuple
import re


class SafetyChecker:
    """命令安全检查器"""
    
    # 危险命令模式（高风险）
    DANGEROUS_PATTERNS = [
        (r'rm\s+-rf\s+/', '删除根目录'),
        (r'rm\s+-rf\s+\*', '递归删除所有文件'),
        (r'mkfs', '格式化磁盘'),
        (r'dd\s+if=.*of=/dev', '直接写入设备'),
        (r':\(\)\{.*\}', 'Fork炸弹'),
        (r'chmod\s+-R\s+777', '修改所有文件权限为777'),
        (r'chown\s+-R', '递归修改文件所有者'),
        (r'format\s+[cC]:', '格式化C盘'),
        (r'del\s+/[fFsS]\s+\*', '强制删除所有文件'),
    ]
    
    # 警告命令模式（中风险）
    WARNING_PATTERNS = [
        (r'rm\s+', '删除文件'),
        (r'del\s+', '删除文件'),
        (r'move\s+', '移动文件'),
        (r'mv\s+', '移动文件'),
        (r'chmod\s+', '修改文件权限'),
        (r'chown\s+', '修改文件所有者'),
        (r'kill\s+-9', '强制终止进程'),
        (r'taskkill\s+/F', '强制终止进程'),
        (r'shutdown', '关机/重启'),
        (r'reboot', '重启系统'),
        (r'sudo\s+', '使用管理员权限'),
    ]
    
    # 安全命令模式（低风险）
    SAFE_PATTERNS = [
        r'^ls\s*',
        r'^dir\s*',
        r'^pwd\s*',
        r'^cd\s+',
        r'^echo\s+',
        r'^cat\s+',
        r'^type\s+',
        r'^grep\s+',
        r'^find\s+',
        r'^ps\s*',
        r'^top\s*',
        r'^df\s*',
        r'^du\s*',
        r'^whoami\s*',
        r'^date\s*',
        r'^Get-',  # PowerShell Get 命令
        r'^Show-',  # PowerShell Show 命令
    ]
    
    def check_safety(self, command: str) -> Tuple[str, str, str]:
        """
        检查命令安全等级
        
        Args:
            command: 要检查的命令
            
        Returns:
            Tuple[str, str, str]: (风险等级, 风险描述, 颜色代码)
                风险等级: 'high', 'medium', 'low'
                风险描述: 具体的风险说明
                颜色代码: '#ff0000' (红), '#ff9800' (橙), '#4caf50' (绿)
        """
        command = command.strip()
        
        # 检查高风险命令
        for pattern, description in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return (
                    'high',
                    f'高危命令: {description}',
                    '#ff0000'  # 红色
                )
        
        # 检查中风险命令
        for pattern, description in self.WARNING_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return (
                    'medium',
                    f'需谨慎: {description}',
                    '#ff9800'  # 橙色
                )
        
        # 检查低风险命令
        for pattern in self.SAFE_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return (
                    'low',
                    '安全命令',
                    '#4caf50'  # 绿色
                )
        
        # 默认为中等风险
        return (
            'medium',
            '未知命令，请谨慎执行',
            '#ff9800'  # 橙色
        )
    
    def get_safety_tips(self, command: str) -> str:
        """
        获取安全提示
        
        Args:
            command: 命令
            
        Returns:
            str: 安全提示文本
        """
        level, description, _ = self.check_safety(command)
        
        tips = {
            'high': '此命令可能造成严重后果，建议不要执行！',
            'medium': '此命令会修改系统状态，请确认后再执行。',
            'low': '此命令是只读操作，可以安全执行。'
        }
        
        return tips.get(level, '请谨慎执行此命令。')


# 测试代码
if __name__ == '__main__':
    checker = SafetyChecker()
    
    test_commands = [
        'ls -la',
        'rm -rf /',
        'del /f /s *.*',
        'Get-ChildItem',
        'chmod 777 file.txt',
        'echo Hello',
        'shutdown -h now',
    ]
    
    print("=" * 60)
    print("命令安全检查测试")
    print("=" * 60)
    
    for cmd in test_commands:
        level, desc, color = checker.check_safety(cmd)
        tips = checker.get_safety_tips(cmd)
        
        print(f"\n命令: {cmd}")
        print(f"风险等级: {level}")
        print(f"描述: {desc}")
        print(f"提示: {tips}")
        print("-" * 60)
