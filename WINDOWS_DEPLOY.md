# Windows 部署教程 — 图书管理系统

> 本文档面向在 **Windows 10/11** 电脑上首次部署本系统的操作人员。
> 全程只需要**命令行**操作，不需要 Docker、WSL 或 Linux 知识。

---

## 目录

1. [环境要求](#1-环境要求)
2. [第一步：安装 uv 包管理器](#2-第一步安装-uv-包管理器)
3. [第二步：安装 Python 3.12](#3-第二步安装-python-312)
4. [第三步：获取项目代码](#4-第三步获取项目代码)
5. [第四步：配置环境变量](#5-第四步配置环境变量)
6. [第五步：安装依赖](#6-第五步安装依赖)
7. [第六步：初始化数据库](#7-第六步初始化数据库)
8. [第七步：启动服务](#8-第七步启动服务)
9. [第八步：访问系统](#9-第八步访问系统)
10. [日常运维](#10-日常运维)
11. [常见问题排查](#11-常见问题排查)
12. [一键启动脚本](#12-一键启动脚本)

---

## 1. 环境要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows 10（1809+）或 Windows 11 |
| Python | **3.12.x**（必须是 3.12，不能用 3.11 或 3.13） |
| 包管理器 | uv 0.7+ |
| 磁盘空间 | 至少 500 MB（含虚拟环境和依赖） |
| 网络 | 首次安装依赖时需要联网 |

> **重要提示**：本项目内置了 Python 版本检测，如果版本不是 3.12.x，启动时会直接报错并提示。
> 不要跳过 Python 版本安装步骤。

---

## 2. 第一步：安装 uv 包管理器

打开 **PowerShell**（右键"开始"菜单 → "终端"或"Windows PowerShell"），执行：

```powershell
powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

安装完成后，**关闭并重新打开** PowerShell，验证安装：

```powershell
uv --version
```

应输出类似 `uv 0.7.x` 的版本号。如果提示"找不到命令"，请重新打开一个终端窗口再试。

---

## 3. 第二步：安装 Python 3.12

通过 uv 安装指定版本的 Python（无需手动去官网下载）：

```powershell
uv python install 3.12
```

验证安装：

```powershell
uv python list
```

输出中应包含 `cpython-3.12.x-windows-x86_64` 字样。

> **为什么不能用其他版本？**
>
> - Python 3.13 修改了部分内部 API，某些依赖包可能尚未适配。
> - Python 3.11 缺少本项目使用的部分标准库特性。
> - 版本不对时依赖解析和运行都可能出错。
> - uv 会自动根据项目 `.python-version` 文件选择 3.12，无需手动切换。

---

## 4. 第三步：获取项目代码

将项目文件夹复制到目标机器上的任意位置，例如：

```
C:\library-system\
```

然后在 PowerShell 中进入该目录：

```powershell
cd C:\library-system
```

如果是通过 Git 获取：

```powershell
git clone <仓库地址> C:\library-system
cd C:\library-system
```

---

## 5. 第四步：配置环境变量

项目通过 `.env` 文件读取配置。复制模板文件：

```powershell
Copy-Item .env.example .env
```

然后用记事本编辑 `.env` 文件：

```powershell
notepad .env
```

### 必须修改的配置

```ini
# 【必改】生产环境密钥，替换为一串随机字符串（至少 50 位）
SECRET_KEY=这里换成你自己的随机密钥

# 【必改】生产环境设为 False
DEBUG=False

# 【必改】填入服务器的 IP 或域名，多个用逗号分隔
ALLOWED_HOSTS=127.0.0.1,localhost,192.168.1.100
```

### 可选配置

```ini
# 数据库地址，默认连接本地 MySQL
DATABASE_URL=mysql://root:123456@127.0.0.1:3306/library

# 智谱 AI 接口密钥（AI 智能搜索功能需要）
ZHIPUAI_API_KEY=your-api-key-here

# 监听地址，0.0.0.0 表示允许局域网其他电脑访问
HOST=0.0.0.0

# 监听端口
PORT=8000

# 服务线程数，默认 4，并发高时可增大
WAITRESS_THREADS=4
```

> **生成随机密钥的方法**：
>
> ```powershell
> uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```
>
> 将输出的字符串粘贴到 `SECRET_KEY=` 后面即可。

---

## 6. 第五步：安装依赖

```powershell
uv sync
```

此命令会自动：
1. 创建虚拟环境（`.venv` 目录）
2. 使用 Python 3.12 安装所有依赖包
3. 在 Windows 上会自动跳过 `gunicorn`（该包仅限 Linux/macOS）

> **离线或公司内网环境？** 见 [11.4 离线环境安装依赖](#114-离线环境安装依赖)。

---

## 7. 第六步：初始化数据库

### 7.0 启动 MySQL

本项目使用 MySQL 数据库。如果使用 Docker 运行 MySQL：

```powershell
docker run -d --name mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=123456 mysql:8.0
```

然后执行建库脚本：

```powershell
docker exec -i mysql mysql -uroot -p123456 < init_db.sql
```

### 7.1 执行数据库迁移

```powershell
uv run python manage.py migrate
```

### 7.1.1 导入演示数据（可选）

```powershell
docker exec -i mysql mysql -uroot -p123456 library < init_data.sql
```

演示账号（密码均为 `Demo@123456`）：
- `demo_admin` — 管理员
- `demo_librarian` — 图书管理员
- `demo_reader` — 普通读者

### 7.2 收集静态资源

```powershell
uv run python manage.py collectstatic --noinput
```

### 7.3 创建管理员账号

```powershell
uv run python manage.py createsuperuser
```

按提示输入用户名、邮箱和密码。

---

## 8. 第七步：启动服务

```powershell
uv run python serve.py
```

看到类似以下输出即表示启动成功：

```
INFO:waitress:Serving on http://0.0.0.0:8000
```

> **注意事项**：
> - 本项目在 Windows 上使用 **Waitress** 作为 WSGI 服务器，不使用 Gunicorn。
> - 不要在 Windows 上运行 `gunicorn` 命令，它不支持 Windows（项目已内置平台检测，误用会给出提示）。
> - 关闭 PowerShell 窗口 = 停止服务。如需后台运行，见 [10.2 设置为 Windows 服务](#102-设置为-windows-服务)。

---

## 9. 第八步：访问系统

在浏览器中打开：

| 访问场景 | 地址 |
|----------|------|
| 本机访问 | `http://127.0.0.1:8000` |
| 局域网其他电脑访问 | `http://<本机IP>:8000` |
| 管理后台 | `http://127.0.0.1:8000/admin` |

> 如果局域网其他电脑无法访问，请检查：
> 1. `.env` 中 `ALLOWED_HOSTS` 是否包含本机 IP
> 2. Windows 防火墙是否放行了 8000 端口（见 [11.6](#116-局域网其他电脑无法访问)）

---

## 10. 日常运维

### 10.1 停止与重启服务

- **停止**：在运行 `serve.py` 的 PowerShell 窗口按 `Ctrl + C`
- **重启**：重新执行 `uv run python serve.py`

### 10.2 设置为 Windows 服务

如果希望系统开机自动启动且不依赖终端窗口，可以使用 **NSSM**（Non-Sucking Service Manager）：

```powershell
# 1. 下载 NSSM：https://nssm.cc/download
# 2. 解压后将 nssm.exe 所在目录加入 PATH，或直接在解压目录运行

# 3. 安装服务（以管理员身份运行 PowerShell）
nssm install LibrarySystem

# 4. 在弹出的界面中填写：
#    Path:         C:\library-system\.venv\Scripts\python.exe
#    Startup Dir:  C:\library-system
#    Arguments:    serve.py
#
#    切到 Environment 选项卡，填入环境变量（每行一个）：
#    DJANGO_SETTINGS_MODULE=core.settings
#    HOST=0.0.0.0
#    PORT=8000

# 5. 启动服务
nssm start LibrarySystem
```

### 10.3 更新项目代码后

```powershell
cd C:\library-system
uv sync
uv run python manage.py migrate
uv run python manage.py collectstatic --noinput
# 重启服务
uv run python serve.py
```

### 10.4 备份数据库

项目使用 MySQL 数据库，使用 `mysqldump` 备份：

```powershell
docker exec mysql mysqldump -uroot -p123456 library > "library_backup_$(Get-Date -Format 'yyyyMMdd').sql"
```

---

## 11. 常见问题排查

### 11.1 启动时提示"Python 版本不对"

```
[启动失败] 当前 Python 版本为 3.13.x，本项目要求 Python 3.12.x。
```

**解决**：安装 Python 3.12：

```powershell
uv python install 3.12
```

然后重新同步环境：

```powershell
uv sync
uv run python serve.py
```

uv 会自动根据项目 `.python-version` 文件选择 3.12。

### 11.2 `uv sync` 时某个包安装失败

常见于 `pandas`、`Pillow` 等含 C 扩展的包。可能原因：

| 原因 | 解决方法 |
|------|----------|
| 网络超时 | 重试 `uv sync`，或配置国内镜像（见下方） |
| 公司代理/防火墙 | 设置 `HTTP_PROXY` 和 `HTTPS_PROXY` 环境变量 |
| 缺少编译工具 | uv 默认下载预编译轮子，通常不需要编译；如仍失败，安装 [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) |

**配置国内 PyPI 镜像**（加速下载）：

在项目根目录创建或编辑 `uv.toml`：

```toml
[[index]]
url = "https://mirrors.aliyun.com/pypi/simple/"
default = true
```

然后重新运行 `uv sync`。

> **即使 pandas/Pillow 未安装成功**，系统的核心功能（登录、借阅、查看图书）仍可正常使用。
> 只有"数据导出"和"头像缩放"功能会受影响，并会给出明确的错误提示。

### 11.3 误执行了 gunicorn 命令

```
[错误] Gunicorn 不支持 Windows 系统。
请改用 Waitress 启动: python serve.py
```

这是正常的保护机制。在 Windows 上请始终使用：

```powershell
uv run python serve.py
```

### 11.4 离线环境安装依赖

如果目标机器无法联网，可在有网的电脑上预先下载依赖包：

```powershell
# === 在有网的电脑上执行 ===

# 1. 导出依赖包到 vendor 目录
uv export --format requirements-txt --no-hashes > requirements-export.txt
uv pip download -r requirements-export.txt -d vendor --python-platform windows --python-version 3.12

# 2. 将项目目录（含 vendor 文件夹）整体复制到目标机器
```

```powershell
# === 在离线的目标机器上执行 ===

cd C:\library-system
uv python install 3.12           # 如已安装可跳过（需提前安装 uv 和 Python）
uv venv
uv pip install --no-index --find-links vendor -r requirements-export.txt
uv run python manage.py migrate
uv run python manage.py collectstatic --noinput
uv run python serve.py
```

### 11.5 端口被占用

```
OSError: [Errno 10048] 端口已被使用
```

修改 `.env` 中的 `PORT` 为其他值，例如：

```ini
PORT=9000
```

或者查找并停止占用端口的进程：

```powershell
netstat -ano | findstr :8000
taskkill /PID <进程ID> /F
```

### 11.6 局域网其他电脑无法访问

**检查清单**：

1. **`.env` 配置**：`ALLOWED_HOSTS` 中包含本机局域网 IP

   ```ini
   ALLOWED_HOSTS=127.0.0.1,localhost,192.168.1.100
   ```

2. **防火墙放行端口**（以管理员身份运行 PowerShell）：

   ```powershell
   New-NetFirewallRule -DisplayName "Library System" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
   ```

3. **查看本机 IP**：

   ```powershell
   ipconfig
   ```

   找到"IPv4 地址"一行，告知访问方使用该 IP。

### 11.7 页面样式丢失（CSS/JS 未加载）

执行静态资源收集：

```powershell
uv run python manage.py collectstatic --noinput
```

然后重启服务。

### 11.8 数据库迁移报错

如果 `migrate` 失败，可能是数据库表结构冲突。尝试：

```powershell
# 备份现有数据
docker exec mysql mysqldump -uroot -p123456 library > library_backup.sql

# 删除并重建数据库
docker exec -i mysql mysql -uroot -p123456 < init_db.sql
uv run python manage.py migrate
uv run python manage.py createsuperuser
```

> 此操作会丢失所有数据，请务必先备份。

---

## 12. 一键启动脚本

将以下内容保存为项目根目录下的 `start.bat`，双击即可启动：

```bat
@echo off
chcp 65001 >nul
title Library System

cd /d "%~dp0"

echo ========================================
echo   图书管理系统 - 启动中...
echo ========================================
echo.

echo [1/4] 检查 uv ...
where uv >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [错误] 未找到 uv，请先安装:
    echo   powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
    pause
    exit /b 1
)

echo [2/4] 安装依赖 ...
uv sync --frozen
if %ERRORLEVEL% neq 0 (
    echo [警告] uv sync --frozen 失败，尝试 uv sync ...
    uv sync
)

echo [3/4] 数据库迁移 ...
uv run python manage.py migrate

echo [4/4] 收集静态资源 ...
uv run python manage.py collectstatic --noinput

echo.
echo ========================================
echo   启动完成！访问 http://127.0.0.1:8000
echo   按 Ctrl+C 停止服务
echo ========================================
echo.

uv run python serve.py
pause
```

---

## 快速参考卡片

```
安装 uv        powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
安装 Python    uv python install 3.12
安装依赖       uv sync
数据库迁移     uv run python manage.py migrate
创建管理员     uv run python manage.py createsuperuser
收集静态资源   uv run python manage.py collectstatic --noinput
启动服务       uv run python serve.py
开发调试       uv run python manage.py runserver 0.0.0.0:8000
```
