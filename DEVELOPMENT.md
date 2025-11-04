开发手册（AI-AssistedTrainingWebsite）

目录
- 开发环境与启动
- 静态资源（CSS/JS/图片）
- 模板与样式规范
- 缓存与版本号策略
- 数据库迁移规范
- ASGI/WSGI 与部署建议
- 调试与排错清单
- 常见问题（FAQ）

开发环境与启动
- Python: 3.10+（建议与当前 venv 保持一致）
- 依赖：见 `requirements.txt`（如需补充：pymysql、channels、django-filter、simpleui 等）
- 本地启动（开发）：
  - 激活虚拟环境后在项目根目录执行：
    - `python manage.py migrate`
    - （如需）`python manage.py createsuperuser`
    - `python manage.py runserver`
- 后端设置位于 `English_Listening_Website/settings.py`

静态资源（CSS/JS/图片）
- 统一通过 Django 模板标签引用：
  - 顶部：`{% load static %}`
  - 引用：`<link rel="stylesheet" href="{% static 'css/xxx.css' %}">`
- 项目关键配置：
  - `STATIC_URL = '/static/'`
  - 开发环境 URL 注册：见 `English_Listening_Website/urls.py` 中 `staticfiles_urlpatterns()`
- 本项目在开发模式下增加了 MIME 修正与缓存控制：
  - `settings.py` 中：
    - `mimetypes.add_type('text/css', '.css', strict=True)`
  - `English_Listening_Website/middleware.py` 中：
    - `StaticFileContentTypeMiddleware` 确保 `.css` 返回 `text/css; charset=utf-8`，并在 DEBUG 下禁用缓存
- 字体与第三方前端库（如 SimpleUI、FontAwesome、ElementUI）也通过 `/static/` 提供，注意路径是否正确落在 `static/` 目录树下

模板与样式规范
- HTML 模板：以 app 模板目录为单位（如 `ELW/templates/`）。
- 样式放外部 CSS，必要时可添加“动态加载 CSS”的兜底脚本，避免浏览器错误缓存导致不解析。
- 尽量避免滥用 `!important`；若与第三方样式冲突，优先用更具体选择器解决。

缓存与版本号策略
- 开发阶段：已通过中间件对 `.css` 禁用缓存；仍可在链接后附加时间戳强制刷新：
  - 如：`{% static 'css/login.css' %}?v={{ timestamp }}` 或手动 `?v=Date.now()`
- 生产阶段：建议采用文件指纹（hash）或收敛到 WhiteNoise/Nginx 长缓存策略（见“部署建议”）

数据库迁移规范
- 修改模型后：
  - `python manage.py makemigrations`
  - `python manage.py migrate`
- 跨 app 依赖要特别注意：
  - 例如 `stu_practice` 依赖 `accessment` 时，依赖的迁移号必须存在；避免引用被删除或未提交的迁移文件。
- 遇到迁移链断裂（NodeNotFoundError）：
  - 找到报错迁移文件，修正 `dependencies` 中的目标迁移号（如改为已存在的 `0001_initial`），或补齐缺失迁移。

ASGI/WSGI 与部署建议
- 开发：`runserver`（ASGI/Daphne 也可）。
- 生产：建议前置 Nginx + Gunicorn/Uvicorn，并让 Nginx 直接服务静态文件；或采用 WhiteNoise：
  - `pip install whitenoise`
  - `MIDDLEWARE` 顶部加入 `whitenoise.middleware.WhiteNoiseMiddleware`
  - 配置 `STATIC_ROOT` 并执行 `python manage.py collectstatic`
  - 优点：自动提供压缩与缓存头，避免 MIME 与缓存问题

调试与排错清单
- 样式不生效（首选自检脚本，浏览器 Console 执行）：
  1. 列出样式表与规则数：
     ```javascript
     [...document.styleSheets].filter(s => s.href).map(s => ({href: s.href, rules: s.cssRules?.length}))
     ```
     - 若 `rules` 为 0，浏览器未解析该 CSS。
  2. 检查响应头与内容：
     ```javascript
     fetch('/static/css/login.css', { cache: 'no-store' })
       .then(r => { console.log('status:', r.status, 'type:', r.headers.get('content-type')); return r.text(); })
       .then(t => console.log('len:', t.length))
     ```
     - `type` 应为 `text/css`，长度应大于 0。
  3. 动态加载兜底：
     ```javascript
     (() => { const link = document.createElement('link'); link.rel='stylesheet'; link.type='text/css'; link.href='/static/css/login.css?v=' + Date.now(); document.head.appendChild(link); })();
     ```
- 若仅部分页面（如 `/admin/`）失效：
  - 检查对应第三方 CSS（SimpleUI/ElementUI/FontAwesome）是否 `rules=0`；
  - 使用第 2、3 步排查并强制刷新缓存；确认响应头已为 `text/css`。
- 常见报错：
  - `application/x-css`：浏览器拒绝解析；本项目已通过中间件与 `mimetypes` 修正，若仍遇到，清缓存或追加版本号强制刷新。
  - 404 `favicon.ico`、`/.well-known/...`：无功能影响。

常见问题（FAQ）
1. 登录页样式不生效但 CSS 能访问？
   - 通常是错误的 MIME 或缓存粘连；参考“调试与排错清单”的 1~3 步。项目已默认修正 MIME，并在 DEBUG 下禁用 `.css` 缓存。
2. 管理后台（/admin）样式丢失？
   - 多见于 SimpleUI/ElementUI 的 CSS 被浏览器缓存为错误类型；使用强制刷新或版本号参数；必要时启用动态加载兜底。
3. 迁移报 `NodeNotFoundError`？
   - 修正迁移文件的 `dependencies` 指向存在的迁移，或补齐缺失迁移；
   - 参考已修复示例：`stu_practice.0002` 改为依赖 `('accessment', '0001_initial')`。

附：建议的工作流程
- 修改代码 → 保存 → 页面强制刷新（Ctrl+Shift+R）
- 如遇样式异常 → 先跑调试清单（规则数、MIME、动态加载）
- 如遇迁移异常 → 明确依赖链 → `makemigrations`/`migrate` 按序执行
- 准备上线 → 引入 WhiteNoise 或 Nginx 托管静态资源，执行 `collectstatic`

备注
- 本文档适用于当前代码结构；若后续引入前端构建（如 Vite/Webpack），需追加构建与产物路径说明。


