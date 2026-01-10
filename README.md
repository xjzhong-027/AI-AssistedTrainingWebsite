# AI 辅助听力学习网站

> **项目类型**: Django Web 应用  
> **开发模式**: 前后端分离（服务化架构）  
> **当前状态**: 模块化重构进行中（阶段 4 已完成）

---

## 项目简介

AI 辅助听力学习网站是一个基于 Django 的在线英语听力学习平台，支持教师备课、学生练习、AI 评估、数据分析等功能。项目正在进行模块化重构，采用服务接口层（Service Layer）架构，提高代码的可维护性和可扩展性。

## 技术栈

### 后端
- **框架**: Django 3.x / 4.x
- **数据库**: SQLite / MySQL
- **ORM**: Django ORM
- **架构模式**: 服务接口层（Service Layer）架构
- **测试**: Django Test Framework

### 前端
- **模板引擎**: Django Templates
- **样式**: CSS / SimpleUI
- **JavaScript**: 原生 JS / jQuery

## 项目结构

```
AI-AssistedTrainingWebsite/
├── Account/              # 用户与身份管理模块
│   ├── services/         # 服务实现层
│   ├── models.py        # 数据模型
│   └── views.py         # 视图层
├── ELW/                  # 教师备课与题库模块
│   ├── services/         # 服务实现层
│   └── views.py
├── forum/                # 论坛模块
├── announce/             # 公告模块
├── stu_practice/         # 学生练习模块
├── accessment/           # 考试评估模块
├── Query/                # 数据查询模块
├── AI_module/            # AI 评估模块
├── common/               # 公共模块（服务接口定义）
│   ├── services/         # 服务接口层（抽象基类）
│   └── exceptions.py     # 统一异常定义
├── docs/                 # 项目文档
│   ├── 阶段一_子系统划分.md
│   ├── 阶段二_模块化改进设计.md
│   └── 阶段N完成总结.md
└── English_Listening_Website/  # Django 项目配置
    ├── settings.py
    └── urls.py
```

## 架构设计

### 服务接口层架构

项目采用**服务接口层（Service Layer）**架构模式，借鉴了 Spring Boot 项目的分层设计：

```
Controller/Views 层
    ↓
Service 接口层（common/services/）
    ↓
Service 实现层（各模块的 services/）
    ↓
Repository/Models 层
```

**核心设计原则**：
1. **接口与实现分离**：所有服务接口定义在 `common/services/`，实现分散在各模块
2. **依赖倒置**：上层依赖接口，不依赖具体实现
3. **模块解耦**：模块间通过服务接口通信，避免直接访问其他模块的模型

### 服务接口列表

| 服务接口 | 说明 | 实现模块 | 状态 |
|---------|------|---------|------|
| UserService | 用户信息服务 | Account | ✅ 已完成 |
| AuthService | 认证服务 | Account | 🚧 进行中 |
| ContentService | 内容服务 | ELW | ✅ 已完成 |
| ExamService | 考试服务 | stu_practice/accessment | 📋 待开发 |
| CommunicationService | 通信服务 | forum/announce | 📋 待开发 |
| AIService | AI 服务 | AI_module | 📋 待开发 |
| FileService | 文件服务 | ELW | 📋 待开发 |
| NotificationService | 通知服务 | announce | 📋 待开发 |
| LogService | 日志服务 | Log | 📋 待开发 |
| DataService | 数据查询服务 | Query | 📋 待开发 |

## 开发模式借鉴

本项目借鉴了 **spring期末项目** 的开发模式：

### 1. 分层架构
- **Controller/Views 层**：处理 HTTP 请求，类似 Spring 的 `@RestController`
- **Service 层**：业务逻辑处理，接口与实现分离
- **Repository/Models 层**：数据访问，类似 Spring Data JPA

### 2. 统一响应处理
- 使用统一的异常处理机制（`common/exceptions.py`）
- 服务层抛出业务异常，由上层统一处理

### 3. 测试驱动开发
- **测试先行原则**：先编写测试用例，再实现功能
- 每个服务接口都有对应的测试用例
- 所有代码必须经过用户测试验证后才能合并

### 4. 文档驱动开发
- 详细的开发计划和进度跟踪
- 每个阶段都有完成总结文档
- 问题记录和解决方案文档化

## 快速开始

### 环境要求
- Python 3.10+
- Django 3.x / 4.x
- SQLite / MySQL

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd AI-AssistedTrainingWebsite
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **数据库迁移**
```bash
python manage.py migrate
```

4. **创建超级用户**
```bash
python manage.py createsuperuser
```

5. **运行开发服务器**
```bash
python manage.py runserver
```

6. **访问应用**
- 前端应用：http://localhost:8000
- 管理后台：http://localhost:8000/admin

## 开发进度

### 已完成阶段
- ✅ **阶段 1**：建立服务接口层（定义 10 个服务接口）
- ✅ **阶段 2**：迁移登录功能到 Account 模块
- ✅ **阶段 3**：实现 AuthService 并逐步替换
- ✅ **阶段 4**：实现 UserService 并逐步替换（6 个模块已迁移）

### 进行中阶段
- 🚧 **阶段 5**：实现 ContentService 并逐步替换

### 待开发阶段
- 📋 **阶段 6**：实现其他服务接口（AIService、FileService 等）
- 📋 **阶段 7**：合并重复模块

**总体进度**：4/7 阶段已完成（57.1%）

## 文档结构

### 设计文档
- `docs/阶段一_子系统划分.md` - 子系统划分与模块化分析
- `docs/阶段二_模块化改进设计.md` - 模块化改进设计方案

### 开发文档
- `docs/阶段N开发计划.md` - 各阶段的开发计划
- `docs/阶段N进度.md` - 各阶段的进度跟踪
- `docs/阶段N完成总结.md` - 各阶段的完成总结
- `docs/阶段N验收标准.md` - 各阶段的验收标准

### 问题记录
- `docs/常见问题记录.md` - 开发过程中遇到的常见问题
- `docs/已知问题记录.md` - 已知但未解决的问题

### 其他文档
- `docs/开发任务清单.md` - 总体开发任务清单
- `docs/开发进度.md` - 总体开发进度
- `DEVELOPMENT.md` - 开发手册（环境配置、调试指南等）

## 开发规范

### 测试驱动开发（TDD）
1. 先编写测试用例
2. 运行测试（应该失败）
3. 编写实现代码
4. 运行测试（应该通过）
5. 重构优化

### 测试先行原则
- 所有代码必须经过用户测试验证后才能合并
- 每个服务接口都有对应的测试用例
- 测试覆盖正常流程和异常流程

### 代码组织
- **服务接口**：定义在 `common/services/`
- **服务实现**：实现分散在各模块的 `services/` 目录
- **测试文件**：放在各模块的 `tests/` 目录

## 子系统划分

| 子系统编号 | 子系统名称 | 核心责任 | 主要 Django App |
|-----------|----------|---------|---------------|
| S1 | 用户与身份管理 | 账户生命周期、权限控制 | `Account` |
| S2 | 教师备课与题库 | 媒体素材管理、题目生成 | `ELW` |
| S3 | 学生练习与考试 | 练习/考试流程、作答提交 | `stu_practice`, `accessment` |
| S4 | AI 评估与反馈 | AI 模型调用、自动批改 | `AI_module` |
| S5 | 学习评估与数据分析 | 行为数据采集、统计分析 | `Query`, `Log` |
| S6 | 协同与交流 | 论坛、公告、实时消息 | `forum`, `announce` |
| S7 | 基础设施与运维 | 备份、任务调度 | `Backup` |

详细说明请参考：`docs/阶段一_子系统划分.md`

## 贡献指南

1. 遵循测试驱动开发原则
2. 所有代码必须经过测试验证
3. 及时更新相关文档
4. 遵循代码规范和命名规范

## 许可证

[待补充]

## 联系方式

[待补充]

---

**最后更新**: 2024-12  
**文档版本**: v1.0












