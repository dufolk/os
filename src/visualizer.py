#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令执行可视化模块
提供命令执行结果的可视化展示
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QProgressBar, QTextEdit, QGroupBox, QTreeWidget,
    QTreeWidgetItem, QTabWidget
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import re
import os


class CommandVisualizer(QWidget):
    """命令执行可视化组件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 文本输出标签页
        self.text_tab = QWidget()
        self.init_text_tab()
        self.tab_widget.addTab(self.text_tab, "文本输出")
        
        # 文件树标签页
        self.tree_tab = QWidget()
        self.init_tree_tab()
        self.tab_widget.addTab(self.tree_tab, "文件树")
        
        # 统计信息标签页
        self.stats_tab = QWidget()
        self.init_stats_tab()
        self.tab_widget.addTab(self.stats_tab, "统计信息")
    
    def init_text_tab(self):
        """初始化文本输出标签页"""
        layout = QVBoxLayout(self.text_tab)
        
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.setFont(QFont("Consolas", 9))
        layout.addWidget(self.text_output)
    
    def init_tree_tab(self):
        """初始化文件树标签页"""
        layout = QVBoxLayout(self.tree_tab)
        
        info_label = QLabel("文件和目录结构")
        info_label.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(info_label)
        
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["名称", "类型", "大小"])
        self.file_tree.setColumnWidth(0, 300)
        layout.addWidget(self.file_tree)
    
    def init_stats_tab(self):
        """初始化统计信息标签页"""
        layout = QVBoxLayout(self.stats_tab)
        
        # 统计信息组
        stats_group = QGroupBox("执行统计")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_labels = {}
        stat_items = [
            ("total_lines", "总行数"),
            ("total_files", "文件数"),
            ("total_dirs", "目录数"),
            ("total_size", "总大小"),
            ("execution_time", "执行时间"),
        ]
        
        for key, label in stat_items:
            h_layout = QHBoxLayout()
            label_widget = QLabel(f"{label}:")
            label_widget.setMinimumWidth(100)
            value_widget = QLabel("0")
            value_widget.setStyleSheet("font-weight: bold; color: #2196F3;")
            h_layout.addWidget(label_widget)
            h_layout.addWidget(value_widget)
            h_layout.addStretch()
            stats_layout.addLayout(h_layout)
            self.stats_labels[key] = value_widget
        
        layout.addWidget(stats_group)
        layout.addStretch()
    
    def visualize_output(self, command: str, output: str, status: str):
        """
        可视化命令输出
        
        Args:
            command: 执行的命令
            output: 命令输出
            status: 执行状态
        """
        # 显示文本输出
        self.text_output.setPlainText(output)
        
        # 根据命令类型选择可视化方式
        command_lower = command.lower().strip()
        
        if self._is_file_list_command(command_lower):
            self._visualize_file_list(output)
        elif self._is_process_command(command_lower):
            self._visualize_process_list(output)
        else:
            self._visualize_generic(output)
        
        # 更新统计信息
        self._update_statistics(output)
    
    def _is_file_list_command(self, command: str) -> bool:
        """判断是否是文件列表命令"""
        file_commands = ['dir', 'ls', 'get-childitem', 'tree', 'find']
        return any(cmd in command for cmd in file_commands)
    
    def _is_process_command(self, command: str) -> bool:
        """判断是否是进程命令"""
        process_commands = ['ps', 'tasklist', 'get-process', 'top']
        return any(cmd in command for cmd in process_commands)
    
    def _visualize_file_list(self, output: str):
        """可视化文件列表"""
        self.file_tree.clear()
        
        lines = output.strip().split('\n')
        
        # 解析 dir 命令输出 (Windows)
        for line in lines:
            line = line.strip()
            if not line or line.startswith('驱动器') or line.startswith('目录'):
                continue
            
            # 尝试解析文件信息
            parts = line.split()
            if len(parts) >= 4:
                try:
                    # Windows dir 格式: 日期 时间 <DIR>/大小 文件名
                    if '<DIR>' in line:
                        file_type = "目录"
                        size = "-"
                        name = ' '.join(parts[3:])
                    else:
                        file_type = "文件"
                        # 尝试提取大小
                        size_match = re.search(r'(\d[\d,]*)\s+(\S+)$', line)
                        if size_match:
                            size = size_match.group(1)
                            name = size_match.group(2)
                        else:
                            size = parts[2] if len(parts) > 2 else "-"
                            name = parts[-1]
                    
                    item = QTreeWidgetItem([name, file_type, size])
                    self.file_tree.addTopLevelItem(item)
                except:
                    pass
        
        # 如果没有解析到内容，显示原始输出
        if self.file_tree.topLevelItemCount() == 0:
            item = QTreeWidgetItem(["原始输出", "文本", "-"])
            self.file_tree.addTopLevelItem(item)
    
    def _visualize_process_list(self, output: str):
        """可视化进程列表"""
        self.file_tree.clear()
        self.file_tree.setHeaderLabels(["进程名", "PID", "内存"])
        
        lines = output.strip().split('\n')
        
        for line in lines[1:]:  # 跳过标题行
            parts = line.split()
            if len(parts) >= 2:
                try:
                    name = parts[0]
                    pid = parts[1] if len(parts) > 1 else "-"
                    mem = parts[4] if len(parts) > 4 else "-"
                    
                    item = QTreeWidgetItem([name, pid, mem])
                    self.file_tree.addTopLevelItem(item)
                except:
                    pass
    
    def _visualize_generic(self, output: str):
        """通用可视化"""
        self.file_tree.clear()
        self.file_tree.setHeaderLabels(["内容", "类型", "值"])
        
        lines = output.strip().split('\n')
        for i, line in enumerate(lines[:50], 1):  # 最多显示50行
            item = QTreeWidgetItem([line[:100], "文本", f"第{i}行"])
            self.file_tree.addTopLevelItem(item)
    
    def _update_statistics(self, output: str):
        """更新统计信息"""
        lines = output.strip().split('\n')
        
        # 统计行数
        self.stats_labels['total_lines'].setText(str(len(lines)))
        
        # 统计文件和目录数
        file_count = len(re.findall(r'<DIR>', output))
        dir_count = len(re.findall(r'<DIR>', output))
        
        self.stats_labels['total_files'].setText(str(file_count))
        self.stats_labels['total_dirs'].setText(str(dir_count))
        
        # 统计总大小
        size_matches = re.findall(r'(\d[\d,]+)\s+字节', output)
        if size_matches:
            total_size = sum(int(s.replace(',', '')) for s in size_matches)
            self.stats_labels['total_size'].setText(self._format_size(total_size))
        else:
            self.stats_labels['total_size'].setText("-")
        
        # 执行时间（这里简化处理）
        self.stats_labels['execution_time'].setText("< 1s")
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def clear(self):
        """清空显示"""
        self.text_output.clear()
        self.file_tree.clear()
        for label in self.stats_labels.values():
            label.setText("0")


# 测试代码
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    visualizer = CommandVisualizer()
    visualizer.setWindowTitle("命令执行可视化")
    visualizer.resize(800, 600)
    
    # 测试数据
    test_output = """
 驱动器 C 中的卷是 Windows
 卷的序列号是 1234-5678

 C:\\Users\\Test 的目录

2024/10/30  10:00    <DIR>          .
2024/10/30  10:00    <DIR>          ..
2024/10/30  09:30             1,234 file1.txt
2024/10/30  09:31             5,678 file2.py
2024/10/30  09:32    <DIR>          folder1
               2 个文件          6,912 字节
               3 个目录
    """
    
    visualizer.visualize_output("dir", test_output, "success")
    visualizer.show()
    
    sys.exit(app.exec())
