# 智能 Shell 助手

基于大模型的智能 Shell 命令助手，可以将自然语言转换为 Shell 命令并执行。

## 功能特性

- ✅ **自然语言转命令**: 用自然语言描述需求，自动生成对应的 Shell 命令
- ✅ **跨平台支持**: 支持 Windows、Linux、macOS
- ✅ **命令解释**: 自动解释生成的命令的作用
- ✅ **安全检查**: 自动检测危险命令，防止误操作
- ✅ **历史记录**: 保存命令执行历史，支持查询和导出
- ✅ **交互模式**: 支持交互式对话和单命令模式
- ✅ **上下文记忆**: 记住之前的命令，提供更智能的建议
- ✅ **图形界面**: 提供基于 PyQt6 的现代化 GUI 界面（适合演示）

## 项目结构

```
os/
├── src/
│   ├── main.py              # 命令行主程序入口
│   ├── gui_main.py          # GUI 主程序（新增）
│   ├── llm_interface.py     # LLM 接口（需要完成）
│   ├── command_executor.py  # 命令执行模块
│   ├── history_manager.py   # 历史记录管理
│   └── config.py            # 配置管理
├── run_gui.py              # GUI 启动器（新增）
├── requirements.txt         # 依赖包
├── config.json             # 配置文件（首次运行后生成）
├── shell_history.json      # 历史记录（首次运行后生成）
├── README.md               # 本文档
└── GUI_README.md           # GUI 使用说明（新增）
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

**推荐使用通义千问（Qwen）:**

**Windows (PowerShell):**
```powershell
$env:DASHSCOPE_API_KEY="your-api-key-here"
```

**Windows (CMD):**
```cmd
set DASHSCOPE_API_KEY=your-api-key-here
```

**Linux/macOS:**
```bash
export DASHSCOPE_API_KEY="your-api-key-here"
```

> 💡 **获取通义千问 API Key**: 访问 https://dashscope.aliyun.com/ 注册并获取免费 API Key
> 
> 📖 **详细配置说明**: 查看 [QWEN_SETUP.md](QWEN_SETUP.md)

**或使用其他大模型（需修改代码）:**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 3. 测试配置

运行测试脚本验证配置是否正确：

```bash
python test_qwen.py
```

如果所有测试通过，说明配置成功！

> ✅ **通义千问接口已实现**: `src/llm_interface.py` 已经完成了通义千问的集成，可以直接使用

### 4. 运行程序

**GUI 模式（推荐用于演示）:**
```bash
python run_gui.py
```

**命令行交互模式:**
```bash
python src/main.py
```

**单命令模式:**
```bash
python src/main.py 显示当前目录下的所有文件
```

**自动执行（不询问确认）:**
```bash
python src/main.py -y 查看系统内存使用情况
```

## 使用示例

### GUI 模式

启动 GUI 后，你将看到一个现代化的图形界面：

1. 在输入框中输入自然语言描述
2. 点击"分析命令"按钮
3. 查看生成的命令和解释
4. 点击"执行命令"按钮（需要确认）
5. 在右侧查看历史记录和统计信息

详细使用说明请参考 [GUI_README.md](GUI_README.md)

### 命令行交互模式

```
$ python src/main.py

============================================================
智能 Shell 助手 - 交互式模式
============================================================
输入自然语言描述，我会帮你生成并执行Shell命令
特殊命令:
  exit/quit - 退出程序
  history   - 查看历史记录
  clear     - 清空屏幕
============================================================

🤖 请输入 > 显示当前目录下的所有文件

🔍 正在分析: 显示当前目录下的所有文件

💡 建议命令: ls -la
📝 解释: 列出当前目录下所有文件（包括隐藏文件）的详细信息

即将执行命令: ls -la
是否执行? (y/n): y

✅ 执行成功:
total 32
drwxr-xr-x  5 user  staff   160 May 10 10:00 .
drwxr-xr-x  8 user  staff   256 May  9 15:30 ..
-rw-r--r--  1 user  staff  1024 May 10 09:55 file1.txt
-rw-r--r--  1 user  staff  2048 May 10 09:58 file2.txt
```

### 单命令模式

```bash
# 查询模式（不执行）
$ python src/main.py 查找所有 Python 文件

🔍 正在分析: 查找所有 Python 文件

💡 建议命令: find . -name "*.py"
📝 解释: 在当前目录及子目录中查找所有 .py 文件

# 自动执行模式
$ python src/main.py -y 查看磁盘使用情况

🔍 正在分析: 查看磁盘使用情况

💡 建议命令: df -h
📝 解释: 以人类可读的格式显示磁盘使用情况

✅ 执行成功:
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1       100G   45G   50G  48% /
```

## 配置说明

编辑 `config.json` 文件可以自定义配置:

```json
{
  "model_name": "gpt-4",
  "temperature": 0.3,
  "max_tokens": 1000,
  "command_timeout": 30,
  "auto_confirm": false,
  "max_history_records": 100,
  "enable_dangerous_command_check": true,
  "allow_destructive_commands": false,
  "show_warnings": true,
  "color_output": true
}
```

**配置项说明:**

- `model_name`: 大模型名称
- `temperature`: 生成随机性（0-1，越低越确定）
- `max_tokens`: 最大生成 token 数
- `command_timeout`: 命令执行超时时间（秒）
- `auto_confirm`: 是否自动执行命令
- `max_history_records`: 最大历史记录数
- `enable_dangerous_command_check`: 是否启用危险命令检查
- `allow_destructive_commands`: 是否允许破坏性命令
- `show_warnings`: 是否显示警告信息
- `color_output`: 是否启用彩色输出

## 历史记录

查看历史记录:
```bash
python src/main.py --history
```

历史记录保存在 `shell_history.json` 文件中，格式如下:
```json
[
  {
    "timestamp": "2024-05-10T10:00:00",
    "user_input": "显示当前目录",
    "command": "ls -la",
    "status": "success",
    "output": "...",
    "error": "",
    "return_code": 0
  }
]
```

## 安全特性

1. **危险命令检测**: 自动识别危险命令（如 `rm -rf /`）并警告
2. **执行确认**: 默认需要用户确认才执行命令
3. **超时保护**: 命令执行超时自动终止
4. **权限检查**: 检测并提示权限不足的操作

## 开发说明

### 需要完成的部分

打开 [src/llm_interface.py](src/llm_interface.py)，完成以下函数:

1. **`natural_language_to_command()`** - 核心功能，必须实现
2. **`explain_command()`** - 可选，解释命令作用
3. **`suggest_fix()`** - 可选，命令失败后给出修复建议

### LLM 接口要求

返回格式必须是:
```python
{
    'command': 'ls -la',              # 生成的命令
    'explanation': '列出所有文件',      # 命令解释
    'warnings': ['包含隐藏文件'],       # 警告信息（可选）
    'error': None                      # 错误信息（如果有）
}
```

### 测试模块

每个模块都可以单独测试:

```bash
# 测试命令执行器
python src/command_executor.py

# 测试历史记录管理
python src/history_manager.py

# 测试配置管理
python src/config.py
```

## 扩展功能建议

- [ ] 支持多轮对话，实现复杂任务分解
- [ ] 添加命令模板库，加速常用命令生成
- [ ] 集成代码补全功能
- [ ] 添加命令执行结果的可视化展示
- [ ] 支持命令执行计划（定时任务）
- [ ] 添加命令风险评分系统
- [ ] 支持插件系统，扩展功能

## 常见问题

**Q: 如何更换大模型？**
A: 修改 `src/llm_interface.py` 中的实现，支持任何兼容的 LLM API（如 Claude、通义千问等）。

**Q: 命令执行失败怎么办？**
A: 检查命令语法、权限、系统兼容性。可以实现 `suggest_fix()` 函数自动给出修复建议。

**Q: 如何禁用危险命令检查？**
A: 在 `config.json` 中设置 `"enable_dangerous_command_check": false`，但不推荐。

**Q: 支持哪些操作系统？**
A: Windows（cmd/PowerShell）、Linux、macOS 均支持。

## 课程报告建议

### 报告结构

1. **项目背景与意义**
   - 操作系统课程结合 AI 技术
   - 提高命令行操作效率
   - 降低学习门槛

2. **系统设计**
   - 整体架构图
   - 模块划分说明
   - 数据流程图

3. **核心功能实现**
   - 自然语言处理（LLM 调用）
   - 命令执行与安全控制
   - 历史记录管理

4. **测试与演示**
   - 功能测试用例
   - 性能测试
   - 实际使用场景演示

5. **总结与展望**
   - 实现的功能
   - 遇到的问题与解决方案
   - 未来改进方向

### 演示建议

准备 3-5 个典型场景:
1. 文件操作（查找、复制、移动）
2. 系统监控（CPU、内存、磁盘）
3. 网络操作（ping、端口扫描）
4. 进程管理（查看、终止进程）
5. 危险命令拦截演示

## 许可证

MIT License

## 作者

[你的名字] - 操作系统课程项目

## 致谢

- 大模型技术支持
- 操作系统课程指导
