#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史记录管理模块
负责保存和查询命令执行历史
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class HistoryManager:
    """历史记录管理器"""

    def __init__(self, config):
        """
        初始化历史记录管理器

        Args:
            config: 配置对象
        """
        self.config = config
        self.history_file = config.history_file if hasattr(config, 'history_file') else 'shell_history.json'
        self.max_records = config.max_history_records if hasattr(config, 'max_history_records') else 100
        self.history = self._load_history()

    def add_record(self, user_input: str, command: str, result: Dict):
        """
        添加一条历史记录

        Args:
            user_input: 用户输入的自然语言
            command: 执行的Shell命令
            result: 执行结果字典
        """
        record = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'command': command,
            'status': result.get('status', 'unknown'),
            'output': result.get('output', '')[:500],  # 限制输出长度
            'error': result.get('error', ''),
            'return_code': result.get('return_code', -1)
        }

        self.history.append(record)

        # 限制历史记录数量
        if len(self.history) > self.max_records:
            self.history = self.history[-self.max_records:]

        # 保存到文件
        self._save_history()

    def get_recent_context(self, limit: int = 5) -> List[Dict]:
        """
        获取最近的历史记录作为上下文

        Args:
            limit: 返回的记录数量

        Returns:
            List[Dict]: 历史记录列表
        """
        return self.history[-limit:] if len(self.history) > 0 else []

    def get_all_history(self) -> List[Dict]:
        """
        获取所有历史记录

        Returns:
            List[Dict]: 所有历史记录
        """
        return self.history

    def clear_history(self):
        """清空历史记录"""
        self.history = []
        self._save_history()

    def search_history(self, keyword: str) -> List[Dict]:
        """
        搜索历史记录

        Args:
            keyword: 搜索关键词

        Returns:
            List[Dict]: 匹配的历史记录
        """
        keyword_lower = keyword.lower()
        results = []

        for record in self.history:
            if (keyword_lower in record.get('user_input', '').lower() or
                keyword_lower in record.get('command', '').lower()):
                results.append(record)

        return results

    def get_success_rate(self) -> float:
        """
        获取命令执行成功率

        Returns:
            float: 成功率（0-1之间）
        """
        if len(self.history) == 0:
            return 0.0

        success_count = sum(1 for record in self.history if record.get('status') == 'success')
        return success_count / len(self.history)

    def get_statistics(self) -> Dict:
        """
        获取统计信息

        Returns:
            Dict: 统计信息字典
        """
        if len(self.history) == 0:
            return {
                'total_commands': 0,
                'success_count': 0,
                'error_count': 0,
                'success_rate': 0.0
            }

        success_count = sum(1 for record in self.history if record.get('status') == 'success')
        error_count = len(self.history) - success_count

        return {
            'total_commands': len(self.history),
            'success_count': success_count,
            'error_count': error_count,
            'success_rate': success_count / len(self.history),
            'recent_commands': self.get_recent_context(5)
        }

    def _load_history(self) -> List[Dict]:
        """
        从文件加载历史记录

        Returns:
            List[Dict]: 历史记录列表
        """
        if not os.path.exists(self.history_file):
            return []

        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
                # 确保不超过最大记录数
                return history[-self.max_records:] if len(history) > self.max_records else history
        except (json.JSONDecodeError, IOError) as e:
            print(f"警告: 无法加载历史记录文件: {e}")
            return []

    def _save_history(self):
        """保存历史记录到文件"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"警告: 无法保存历史记录: {e}")

    def export_history(self, output_file: str, format: str = 'json'):
        """
        导出历史记录

        Args:
            output_file: 输出文件路径
            format: 导出格式 ('json', 'txt', 'csv')
        """
        try:
            if format == 'json':
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(self.history, f, ensure_ascii=False, indent=2)

            elif format == 'txt':
                with open(output_file, 'w', encoding='utf-8') as f:
                    for i, record in enumerate(self.history, 1):
                        f.write(f"=== 记录 {i} ===\n")
                        f.write(f"时间: {record.get('timestamp', 'N/A')}\n")
                        f.write(f"输入: {record.get('user_input', 'N/A')}\n")
                        f.write(f"命令: {record.get('command', 'N/A')}\n")
                        f.write(f"状态: {record.get('status', 'N/A')}\n")
                        f.write(f"输出: {record.get('output', 'N/A')}\n")
                        f.write("\n")

            elif format == 'csv':
                import csv
                with open(output_file, 'w', encoding='utf-8', newline='') as f:
                    if len(self.history) > 0:
                        writer = csv.DictWriter(f, fieldnames=self.history[0].keys())
                        writer.writeheader()
                        writer.writerows(self.history)

            print(f"历史记录已导出到: {output_file}")

        except IOError as e:
            print(f"导出失败: {e}")


def test_history():
    """测试历史记录管理器"""
    from config import Config

    config = Config()
    history = HistoryManager(config)

    # 添加测试记录
    history.add_record(
        user_input="显示当前目录",
        command="ls -la",
        result={'status': 'success', 'output': 'total 10\ndrwxr-xr-x...', 'error': '', 'return_code': 0}
    )

    history.add_record(
        user_input="查看文件内容",
        command="cat test.txt",
        result={'status': 'error', 'output': '', 'error': 'File not found', 'return_code': 1}
    )

    # 测试功能
    print("最近的记录:")
    for record in history.get_recent_context(2):
        print(f"  - {record['user_input']} -> {record['command']} ({record['status']})")

    print("\n统计信息:")
    stats = history.get_statistics()
    for key, value in stats.items():
        if key != 'recent_commands':
            print(f"  {key}: {value}")


if __name__ == '__main__':
    test_history()
