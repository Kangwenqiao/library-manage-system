# 图书管理系统

这是一个基于 Django 的图书管理系统，现已整理为 `uv` 管理依赖和启动。

## 运行要求

- `uv` 0.7+
- Python `3.9`
- 建议系统：macOS / Linux / Windows WSL

项目已在仓库中固定 `.python-version = 3.9`，不要直接用本机的 Python 3.13 运行。

## 1. 本地开发启动

### 1.1 安装 uv

如果本机还没有安装：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

确认版本：

```bash
uv --version
```

### 1.2 安装 Python 3.9

```bash
uv python install 3.9
```

### 1.3 准备环境变量

```bash
cp .env.example .env
```

默认配置已经可以本地启动，关键变量如下：

- `SECRET_KEY`：Django 密钥，生产环境必须修改
- `DEBUG`：本地开发保持 `True`
- `ROLE_LOGIN_ENABLED`：是否开启登录页角色一键登录，建议仅本地/演示环境开启
- `ALLOWED_HOSTS`：多个值用英文逗号分隔
- `DATABASE_URL`：默认使用 SQLite
- `PORT`：Gunicorn 监听端口，默认 `8000`

### 1.4 安装依赖

```bash
uv sync
```

### 1.5 初始化数据库

```bash
uv run python manage.py migrate
```

如果需要后台账号：

```bash
uv run python manage.py createsuperuser
```

### 1.6 启动开发服务器

```bash
uv run python manage.py runserver 0.0.0.0:8000
```

浏览器访问：

```text
http://127.0.0.1:8000
```

## 2. 生产启动

先收集静态文件并迁移数据库：

```bash
uv run python manage.py collectstatic --noinput
uv run python manage.py migrate
```

再用 Gunicorn 启动：

```bash
uv run gunicorn --config gunicorn-cfg.py core.wsgi
```

默认监听端口为 `8000`，可通过环境变量修改：

```bash
export PORT=9000
export GUNICORN_WORKERS=4
uv run gunicorn --config gunicorn-cfg.py core.wsgi
```

## 3. Docker 部署

项目已经改为 `uv` 风格的 Dockerfile，直接执行：

```bash
docker build -t library-manage-system .
docker run --rm -p 8000:8000 --env-file .env library-manage-system
```

## 4. 常用 uv 命令

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver 0.0.0.0:8000
uv run gunicorn --config gunicorn-cfg.py core.wsgi
```

## 5. Git 忽略说明

当前 `.gitignore` 已经忽略了以下内容：

- 虚拟环境目录，例如 `.venv/`、`authentication/env/`
- 本地数据库文件，例如 `db.sqlite3`
- 上传文件目录 `media/`
- 收集后的静态文件目录 `staticfiles/`
- 运行日志 `logging/*.log`
- 本地环境变量文件 `.env`

## 6. 常见问题

### 6.1 `uv sync` 失败

先确认当前 Python 版本不是系统自带的 `3.13`，而是：

```bash
uv python list
```

如果没有 `3.9`，重新执行：

```bash
uv python install 3.9
```

### 6.2 页面静态资源缺失

执行：

```bash
uv run python manage.py collectstatic --noinput
```

### 6.3 克隆后日志目录不存在导致启动报错

项目已在 `core/settings.py` 中自动创建 `logging/` 目录，正常情况下不需要手动处理。
