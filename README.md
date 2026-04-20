# 图书管理系统

这是一个基于 Django 的图书管理系统，已经整理为 `uv` 管理依赖，并补齐了 Windows 启动兼容。

## 运行要求

- `uv` 0.7+
- Python `3.12`
- 支持 `Windows / macOS / Linux`
- `gunicorn` 仅在非 Windows 平台安装（Windows 使用 `waitress`）

项目固定 `.python-version = 3.12`，不要直接用系统 Python 3.13。

## 1. 开发启动

### 1.1 安装 uv

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

macOS / Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

确认版本：

```bash
uv --version
```

### 1.2 安装 Python 3.12

```bash
uv python install 3.12
```

### 1.3 准备环境变量

Windows CMD:

```cmd
copy .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS / Linux:

```bash
cp .env.example .env
```

关键变量：

- `SECRET_KEY`：Django 密钥，生产环境必须修改
- `DEBUG`：开发环境保持 `True`
- `ALLOWED_HOSTS`：多个值用英文逗号分隔
- `DATABASE_URL`：默认使用 SQLite
- `HOST`：Waitress 监听地址，默认 `0.0.0.0`
- `PORT`：服务端口，默认 `8000`
- `WAITRESS_THREADS`：Windows 和通用部署线程数，默认 `4`

### 1.4 安装依赖

```bash
uv sync
```

### 1.5 初始化数据库

```bash
uv run python manage.py migrate
```

如需后台账号：

```bash
uv run python manage.py createsuperuser
```

### 1.6 启动开发服务器

```bash
uv run python manage.py runserver 0.0.0.0:8000
```

访问：

```text
http://127.0.0.1:8000
```

## 2. 生产启动

先执行：

```bash
uv run python manage.py collectstatic --noinput
uv run python manage.py migrate
```

建议生产环境使用锁定安装：

```bash
uv sync --frozen
```

### 2.1 Windows 推荐启动方式

```bash
uv run python serve.py
```

这个入口基于 `waitress`，支持 Windows。

Windows PowerShell 完整示例：

```powershell
Copy-Item .env.example .env
uv sync --frozen
uv run python manage.py migrate
uv run python manage.py collectstatic --noinput
$env:HOST = "0.0.0.0"
$env:PORT = "8000"
$env:WAITRESS_THREADS = "4"
uv run python serve.py
```

Windows CMD 完整示例：

```cmd
copy .env.example .env
uv sync --frozen
uv run python manage.py migrate
uv run python manage.py collectstatic --noinput
set HOST=0.0.0.0
set PORT=8000
set WAITRESS_THREADS=4
uv run python serve.py
```

### 2.2 通用启动方式

```bash
uv run python serve.py
```

### 2.3 Linux 可选 Gunicorn

如果部署环境是 Linux，并且你明确要用 Gunicorn：

```bash
uv run gunicorn --config gunicorn-cfg.py core.wsgi
```

Linux / macOS 设置端口示例：

```bash
export PORT=9000
uv run python serve.py
```

Windows CMD 设置端口示例：

```cmd
set PORT=9000
uv run python serve.py
```

Windows PowerShell 设置端口示例：

```powershell
$env:PORT = "9000"
uv run python serve.py
```

## 3. 常用命令

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver 0.0.0.0:8000
uv run python serve.py
```

## 4. Git 忽略说明

当前 `.gitignore` 已忽略：

- 虚拟环境目录，例如 `.venv/`、`authentication/env/`
- 本地数据库文件，例如 `db.sqlite3`
- 上传文件目录 `media/`
- 收集后的静态文件目录 `staticfiles/`
- 运行日志 `logging/*.log`
- 本地环境变量文件 `.env`

## 5. 常见问题

### 5.1 Windows 上 `gunicorn` 无法启动

这是正常现象，`gunicorn` 不支持 Windows，且项目已配置为 Windows 不安装 `gunicorn`。请改用：

```bash
uv run python serve.py
```

### 5.2 `uv sync` 失败

先确认 Python 版本：

```bash
uv python list
```

没有 `3.12` 时执行：

```bash
uv python install 3.12
```

### 5.3 页面静态资源缺失

执行：

```bash
uv run python manage.py collectstatic --noinput
```

### 5.4 克隆后日志目录不存在导致启动报错

项目已在 `core/settings.py` 中自动创建 `logging/` 目录。
