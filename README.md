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

###配置
- 修改脚本中的配置信息：

```python
TARGET_URL = "http://你的靶场地址/dvwa/vulnerabilities/sqli_blind/"
COOKIE = "PHPSESSID=你的会话ID; security=low"
```

###运行
```bash
python auto_blind_sql.py
```
