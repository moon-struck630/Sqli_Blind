# Sqli_Blind
一个用于DVWA  布尔盲注的自动化Python脚本。支持数据库名、表名、列名和数据的自动化猜解，并带有进度条显示。

## 项目简介

本项目是一个教育性质的SQL盲注自动化脚本，通过二分法逐字符猜解数据库信息。旨在帮助网络安全学习者理解：

- SQL盲注的原理与利用方法
- 布尔盲注的自动化实现
- 二分法在渗透测试中的应用
- Python面向对象编程在安全工具开发中的实践

**⚠️ 法律声明：本工具仅用于授权测试和教育目的，禁止用于非法攻击！**

## ✨ 功能特性

- ✅ 自动检测目标连接状态
- ✅ 二分法猜解数据库名（带进度条）
- ✅ 自动获取所有表名
- ✅ 自动获取指定表的列名
- ✅ 导出表中所有数据
- ✅ 请求延迟控制，避免被封
- ✅ 详细的调试信息输出
- ✅ 结果自动保存到文件

## 🚀 快速开始

### 环境要求

- Python 3.6+
- 依赖库：requests, tqdm

### 安装

```bash
# 克隆仓库
git clone https://github.com/moon-struck630/auto-sql-blind-injection.git
cd dvwa-blind-sql-injection

# 安装依赖
pip install requests tqdm
```

### 配置
- 修改脚本中的配置信息：

```python
TARGET_URL = "http://你的靶场地址/dvwa/vulnerabilities/sqli_blind/"
COOKIE = "PHPSESSID=你的会话ID; security=low"
```

### 运行
```bash
python auto_blind_sql.py
```

### 使用示例
```text
============================================================
DVWA 布尔盲注自动化利用脚本
============================================================

[*] 测试目标连接...
[✓] 目标连接成功

[*]开始猜解数据库名
[*]正在获取数据库名长度...
    [*]测试长度 > 1?
    [*]测试长度 > 2?
    [✓]找到长度: 4
[+]数据库长度:4

[*]猜解第1个字符...
...
[✓]数据库名: dvwa

[*]开始获取数据库'dvwa'的表名
[+]共有4张表
[*]正在获取第1张表名...
[+] 第 1 张表: access_log
...
```

## 核心原理
### 布尔盲注原理
- 当页面没有直接的数据回显，但存在两种不同的响应状态时，可以通过构造条件判断语句，根据页面状态的差异逐位推断数据。

- 判断逻辑：

1' and 1=1 -- - → 页面显示 "User ID exists" (True)

1' and 1=2 -- - → 页面显示 "User ID is MISSING" (False)

- 二分法优化
传统逐字符猜解需要遍历整个字符集（约70次/字符），二分法只需约7次/字符，效率提升10倍。

## 项目结构
```text
dvwa-blind-sql-injection/
│
├── dvwa_blind_sqli.py      # 主脚本
├── README.md                # 本文档
├── requirements.txt         # 依赖列表
├── dump_result.txt          # 导出数据（运行后生成）
└── screenshots/             # 运行截图
    └── demo.png
```

## 类与方法说明
### DVWABlindSQLInjector (父类)
|方法|说明|
|:---|:---|
|__init__()	|初始化注入器，设置URL、Cookie和延迟|
|_parse_cookie()	|将cookie字符串转为字典|
|send_payload()	|发送payload并判断页面状态（核心方法）|
### AdvancedBlindInjector (子类)
|方法	|说明|
|:---|:---|
|get_database_name()	|获取数据库名|
|get_database_name_with_progress()	|带进度条的数据库名获取|
|get_tables()	|获取所有表名|
|get_columns()	|获取指定表的列名|
|dump_table()	|导出表中数据|
|get_string_length()	|获取字符串长度|
|get_number_value()	|获取数值（表数量、行数等）|
|binary_search_char()	|二分法猜解单个字符|

## 常见问题
### Q1: 脚本运行时报错 "目标连接失败"
- 解决方法：

1. 检查URL是否正确

2. 检查Cookie是否有效（重新登录DVWA获取新的PHPSESSID）

3. 确认DVWA安全级别设置为"low"

### Q2: 猜解速度太慢
- 解决方法：

1. 减小delay参数（如从0.5改为0.2）

2. 优化字符集，只包含可能出现的字符

3. 检查网络延迟

### Q3: 出现 "请求异常" 错误
- 解决方法：

1. 检查网络连接

2. 增加timeout参数

3. 可能是目标服务器限流，适当增加delay
