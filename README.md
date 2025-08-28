# 城市守护者 - 环保纪念网页

一个基于 Flask 的小站：上传妥善处理垃圾的照片，即可获得独一无二的二维码纪念，并将你的名字记录在虚拟纪念碑上。

## 本地运行

1. 创建虚拟环境并安装依赖（Windows PowerShell）：

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. 初始化数据库：

```powershell
python app.py  # 首次运行会自动建库
```

或者使用 Flask CLI：

```powershell
$env:FLASK_APP="app.py"
flask init-db
flask run
```

3. 打开浏览器访问 `http://localhost:5000`

## 目录结构

- `app.py` 应用主文件
- `templates/` 页面模板
- `static/` 静态资源（样式、二维码）
- `uploads/` 上传的图片

## 注意
- 默认使用 SQLite 数据库 `app.db`
- 首次上传会在 `static/rewards/` 生成你的二维码图片

---

## 部署到 Render（推荐）

1. 代码准备
- `requirements.txt` 已包含 `gunicorn`
- 新增 `Procfile`：`web: gunicorn app:app`
- `app.py` 已读取环境变量 `PORT` 和 `FLASK_DEBUG`

2. 推送到 GitHub
- 将本项目提交并推送到 GitHub 仓库

3. 在 Render 创建服务
- 新建 Web Service，连接你的仓库
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`

4. 数据库
- 新建 Render PostgreSQL 实例
- 在 Web Service 的 Environment 里设置：
  - `SECRET_KEY`：随机字符串
  - `DATABASE_URL`：Render Postgres 提供的连接串

5. 持久化上传与二维码
- 在 Web Service 的 Disks 中添加 Persistent Disk
- 挂载路径建议：
  - `/opt/render/project/src/uploads`
  - `/opt/render/project/src/static/rewards`
- 与代码中的目录一致即可（本项目默认就是 `uploads/` 与 `static/rewards/`）

6. 部署完成
- Render 会分配一个公网 URL，直接访问即可
- 测试上传、查看成功页和纪念碑

可选：若希望更弹性与更低成本的存储，可将图片与二维码改为对象存储（如 Cloudinary/S3/R2），只需在代码中将本地保存改为上传到对象存储，并将返回的 URL 存入数据库。 