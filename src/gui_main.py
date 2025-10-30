#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能 Shell 助手 - GUI 界面
基于 PyQt6 的图形用户界面
"""

import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QSplitter,
    QListWidget, QListWidgetItem, QMessageBox, QStatusBar,
    QGroupBox, QCheckBox, QTabWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QTextCursor, QColor, QPalette

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.dirname(__file__))

from command_executor import CommandExecutor
from llm_interface import LLMInterface
from history_manager import HistoryManager
from config import Config
from safety_checker import SafetyChecker
from visualizer import CommandVisualizer


class CommandWorker(QThread):
    """后台执行命令的工作线程"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, executor, command):
        super().__init__()
        self.executor = executor
        self.command = command

    def run(self):
        try:
            result = self.executor.execute(self.command)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class LLMWorker(QThread):
    """后台调用 LLM 的工作线程"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, llm, user_input, context, system_info):
        super().__init__()
        self.llm = llm
        self.user_input = user_input
        self.context = context
        self.system_info = system_info

    def run(self):
        try:
            result = self.llm.natural_language_to_command(
                user_input=self.user_input,
                context=self.context,
                system_info=self.system_info
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class SmartShellGUI(QMainWindow):
    """智能 Shell 助手 GUI 主窗口"""

    def __init__(self):
        super().__init__()
        self.config = Config(debug=False)
        self.llm = LLMInterface(self.config)
        self.executor = CommandExecutor(self.config)
        self.history = HistoryManager(self.config)
        self.safety_checker = SafetyChecker()
        
        self.current_command = ""
        self.llm_worker = None
        self.cmd_worker = None
        
        self.init_ui()
        self.load_history()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("智能 Shell 助手")
        self.setGeometry(100, 100, 1200, 800)
        
        # 设置样式
        self.set_style()
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 标题
        title_label = QLabel("智能 Shell 助手")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 系统信息
        info_label = QLabel(self.get_system_info_text())
        info_label.setStyleSheet("color: #666; padding: 5px;")
        main_layout.addWidget(info_label)
        
        # 创建标签页
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # 主界面标签页
        main_tab = QWidget()
        main_tab_layout = QVBoxLayout(main_tab)
        tab_widget.addTab(main_tab, "主界面")
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_tab_layout.addWidget(splitter)
        
        # 左侧：输入和输出区域
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 输入区域
        input_group = QGroupBox("自然语言输入")
        input_layout = QVBoxLayout(input_group)
        
        self.input_text = QLineEdit()
        self.input_text.setPlaceholderText("请输入自然语言描述，例如：显示当前目录的所有文件")
        self.input_text.setMinimumHeight(40)
        input_font = QFont()
        input_font.setPointSize(11)
        self.input_text.setFont(input_font)
        self.input_text.returnPressed.connect(self.on_analyze_clicked)
        input_layout.addWidget(self.input_text)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.analyze_btn = QPushButton("分析命令")
        self.analyze_btn.setMinimumHeight(35)
        self.analyze_btn.clicked.connect(self.on_analyze_clicked)
        button_layout.addWidget(self.analyze_btn)
        
        self.execute_btn = QPushButton("执行命令")
        self.execute_btn.setMinimumHeight(35)
        self.execute_btn.setEnabled(False)
        self.execute_btn.clicked.connect(self.on_execute_clicked)
        button_layout.addWidget(self.execute_btn)
        
        self.clear_btn = QPushButton("清空")
        self.clear_btn.setMinimumHeight(35)
        self.clear_btn.clicked.connect(self.on_clear_clicked)
        button_layout.addWidget(self.clear_btn)
        
        input_layout.addLayout(button_layout)
        left_layout.addWidget(input_group)
        
        # 命令显示区域
        command_group = QGroupBox("生成的命令")
        command_layout = QVBoxLayout(command_group)
        
        self.command_display = QTextEdit()
        self.command_display.setReadOnly(True)
        self.command_display.setMaximumHeight(120)
        command_font = QFont("Consolas", 10)
        self.command_display.setFont(command_font)
        command_layout.addWidget(self.command_display)
        
        left_layout.addWidget(command_group)
        
        # 输出区域 - 使用可视化组件
        output_group = QGroupBox("执行结果可视化")
        output_layout = QVBoxLayout(output_group)
        
        self.visualizer = CommandVisualizer()
        output_layout.addWidget(self.visualizer)
        
        left_layout.addWidget(output_group)
        
        splitter.addWidget(left_widget)
        
        # 右侧：历史记录
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        history_group = QGroupBox("历史记录")
        history_layout = QVBoxLayout(history_group)
        
        # 历史记录列表
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.on_history_item_clicked)
        history_layout.addWidget(self.history_list)
        
        # 历史记录按钮
        history_btn_layout = QHBoxLayout()
        
        self.refresh_history_btn = QPushButton("刷新")
        self.refresh_history_btn.clicked.connect(self.load_history)
        history_btn_layout.addWidget(self.refresh_history_btn)
        
        self.clear_history_btn = QPushButton("清空历史")
        self.clear_history_btn.clicked.connect(self.on_clear_history_clicked)
        history_btn_layout.addWidget(self.clear_history_btn)
        
        history_layout.addLayout(history_btn_layout)
        
        right_layout.addWidget(history_group)
        splitter.addWidget(right_widget)
        
        # 设置分割器比例
        splitter.setStretchFactor(0, 7)
        splitter.setStretchFactor(1, 3)
        
        # 统计信息标签页
        stats_tab = QWidget()
        stats_layout = QVBoxLayout(stats_tab)
        tab_widget.addTab(stats_tab, "统计信息")
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        stats_layout.addWidget(self.stats_text)
        
        refresh_stats_btn = QPushButton("刷新统计")
        refresh_stats_btn.clicked.connect(self.update_statistics)
        stats_layout.addWidget(refresh_stats_btn)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
        # 自动刷新统计
        self.update_statistics()

    def set_style(self):
        """设置应用样式"""
        style = """
        QMainWindow {
            background-color: #f5f5f5;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #ddd;
            border-radius: 6px;
            margin-top: 10px;
            padding-top: 10px;
            background-color: white;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
        QPushButton:disabled {
            background-color: #cccccc;
            color: #666666;
        }
        QLineEdit {
            border: 2px solid #ddd;
            border-radius: 4px;
            padding: 8px;
            background-color: white;
        }
        QLineEdit:focus {
            border: 2px solid #4CAF50;
        }
        QTextEdit {
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: white;
        }
        QListWidget {
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: white;
        }
        QListWidget::item {
            padding: 8px;
            border-bottom: 1px solid #eee;
        }
        QListWidget::item:selected {
            background-color: #e3f2fd;
            color: black;
        }
        QListWidget::item:hover {
            background-color: #f5f5f5;
        }
        QTabWidget::pane {
            border: 1px solid #ddd;
            background-color: white;
            border-radius: 4px;
        }
        QTabBar::tab {
            background-color: #e0e0e0;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: white;
            font-weight: bold;
        }
        """
        self.setStyleSheet(style)

    def get_system_info_text(self):
        """获取系统信息文本"""
        info = self.executor.get_system_info()
        return f"系统: {info['platform']} | Shell: {info['shell']} | 工作目录: {info['current_dir']}"

    def on_analyze_clicked(self):
        """分析按钮点击事件"""
        user_input = self.input_text.text().strip()
        if not user_input:
            QMessageBox.warning(self, "警告", "请输入自然语言描述")
            return
        
        self.status_bar.showMessage("正在分析...")
        self.analyze_btn.setEnabled(False)
        self.execute_btn.setEnabled(False)
        
        # 获取历史上下文
        context = self.history.get_recent_context(limit=5)
        system_info = self.executor.get_system_info()
        
        # 在后台线程中调用 LLM
        self.llm_worker = LLMWorker(self.llm, user_input, context, system_info)
        self.llm_worker.finished.connect(self.on_llm_finished)
        self.llm_worker.error.connect(self.on_llm_error)
        self.llm_worker.start()

    def on_llm_finished(self, result):
        """LLM 分析完成"""
        self.analyze_btn.setEnabled(True)
        
        if result.get('error'):
            self.status_bar.showMessage(f"错误: {result['error']}")
            self.command_display.setPlainText(f"错误: {result['error']}")
            self.command_display.setStyleSheet("color: #f44336;")
            return
        
        command = result.get('command', '')
        explanation = result.get('explanation', '')
        warnings = result.get('warnings', [])
        
        self.current_command = command
        
        # 安全检查
        safety_level, safety_desc, safety_color = self.safety_checker.check_safety(command)
        safety_tips = self.safety_checker.get_safety_tips(command)
        
        # 显示命令
        display_text = f"命令: {command}\n"
        display_text += f"\n{safety_desc}\n"
        display_text += f"提示: {safety_tips}\n"
        
        if explanation:
            display_text += f"\n解释: {explanation}\n"
        if warnings:
            display_text += f"\n警告: {', '.join(warnings)}\n"
        
        self.command_display.setPlainText(display_text)
        
        # 根据安全等级设置背景色
        if safety_level == 'high':
            self.command_display.setStyleSheet("background-color: #ffebee; border: 2px solid #f44336;")
        elif safety_level == 'medium':
            self.command_display.setStyleSheet("background-color: #fff3e0; border: 2px solid #ff9800;")
        else:
            self.command_display.setStyleSheet("background-color: #e8f5e9; border: 2px solid #4caf50;")
        
        self.execute_btn.setEnabled(True)
        self.status_bar.showMessage(f"分析完成 - {safety_desc}")

    def on_llm_error(self, error_msg):
        """LLM 调用出错"""
        self.analyze_btn.setEnabled(True)
        self.status_bar.showMessage(f"错误: {error_msg}")
        QMessageBox.critical(self, "错误", f"LLM 调用失败:\n{error_msg}")

    def on_execute_clicked(self):
        """执行按钮点击事件"""
        if not self.current_command:
            QMessageBox.warning(self, "警告", "没有可执行的命令")
            return
        
        # 确认执行
        reply = QMessageBox.question(
            self,
            "确认执行",
            f"即将执行命令:\n\n{self.current_command}\n\n是否继续?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        self.status_bar.showMessage("正在执行命令...")
        self.execute_btn.setEnabled(False)
        self.analyze_btn.setEnabled(False)
        
        # 在后台线程中执行命令
        self.cmd_worker = CommandWorker(self.executor, self.current_command)
        self.cmd_worker.finished.connect(self.on_command_finished)
        self.cmd_worker.error.connect(self.on_command_error)
        self.cmd_worker.start()

    def on_command_finished(self, result):
        """命令执行完成"""
        self.execute_btn.setEnabled(True)
        self.analyze_btn.setEnabled(True)
        
        # 保存到历史记录
        self.history.add_record(
            user_input=self.input_text.text(),
            command=self.current_command,
            result=result
        )
        
        # 使用可视化组件显示结果
        if result['status'] == 'success':
            self.visualizer.visualize_output(
                self.current_command,
                result['output'],
                result['status']
            )
            self.status_bar.showMessage("命令执行成功")
        else:
            # 错误时显示文本
            error_output = f"执行失败\n\n{result['error']}"
            self.visualizer.text_output.setPlainText(error_output)
            self.status_bar.showMessage("命令执行失败")
        
        # 刷新历史记录
        self.load_history()
        self.update_statistics()

    def on_command_error(self, error_msg):
        """命令执行出错"""
        self.execute_btn.setEnabled(True)
        self.analyze_btn.setEnabled(True)
        self.status_bar.showMessage(f"错误: {error_msg}")
        QMessageBox.critical(self, "错误", f"命令执行失败:\n{error_msg}")

    def on_clear_clicked(self):
        """清空按钮点击事件"""
        self.input_text.clear()
        self.command_display.clear()
        self.command_display.setStyleSheet("")  # 重置样式
        self.visualizer.clear()
        self.current_command = ""
        self.execute_btn.setEnabled(False)
        self.status_bar.showMessage("已清空")

    def load_history(self):
        """加载历史记录"""
        self.history_list.clear()
        records = self.history.get_recent_context(limit=20)
        
        for record in records:
            timestamp = record.get('timestamp', '')
            user_input = record.get('user_input', 'N/A')
            command = record.get('command', 'N/A')
            status = record.get('status', 'unknown')
            
            # 格式化显示
            status_text = "[成功]" if status == "success" else "[失败]"
            item_text = f"{status_text} {user_input[:30]}..."
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, record)
            self.history_list.addItem(item)

    def on_history_item_clicked(self, item):
        """历史记录项点击事件"""
        record = item.data(Qt.ItemDataRole.UserRole)
        
        # 在命令显示区显示历史命令信息
        details = f"时间: {record.get('timestamp', 'N/A')}\n"
        details += f"输入: {record.get('user_input', 'N/A')}\n"
        details += f"命令: {record.get('command', 'N/A')}\n"
        details += f"状态: {record.get('status', 'N/A')}"
        self.command_display.setPlainText(details)
        
        # 使用可视化组件显示输出
        if record.get('output'):
            self.visualizer.visualize_output(
                record.get('command', ''),
                record.get('output', ''),
                record.get('status', 'unknown')
            )

    def on_clear_history_clicked(self):
        """清空历史记录"""
        reply = QMessageBox.question(
            self,
            "确认清空",
            "确定要清空所有历史记录吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.history.clear_history()
            self.load_history()
            self.update_statistics()
            self.status_bar.showMessage("历史记录已清空")

    def update_statistics(self):
        """更新统计信息"""
        stats = self.history.get_statistics()
        
        stats_text = "=" * 50 + "\n"
        stats_text += "历史记录统计\n"
        stats_text += "=" * 50 + "\n\n"
        stats_text += f"总命令数: {stats['total_commands']}\n"
        stats_text += f"成功执行: {stats['success_count']}\n"
        stats_text += f"执行失败: {stats['error_count']}\n"
        stats_text += f"成功率: {stats['success_rate']:.1%}\n\n"
        
        # 显示最近的命令
        if stats.get('recent_commands'):
            stats_text += "最近执行的命令:\n"
            for record in stats['recent_commands'][:5]:
                cmd = record.get('command', 'N/A')
                status = record.get('status', 'unknown')
                status_text = "[成功]" if status == "success" else "[失败]"
                stats_text += f"  {status_text} {cmd}\n"
        
        self.stats_text.setPlainText(stats_text)


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("智能 Shell 助手")
    app.setOrganizationName("Smart Shell")
    
    # 创建并显示主窗口
    window = SmartShellGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
