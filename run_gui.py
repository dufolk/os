#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能 Shell 助手 - GUI 启动器
快速启动图形界面
"""

import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui_main import main

if __name__ == '__main__':
    print("=" * 60)
    print("智能 Shell 助手 - GUI 模式")
    print("=" * 60)
    print("正在启动图形界面...")
    print()
    
    try:
        main()
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("\n请先安装依赖:")
        print("  pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
